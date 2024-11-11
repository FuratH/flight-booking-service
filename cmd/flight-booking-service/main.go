package main

import (
	"context"
	"errors"
	"net"
	"net/http"
	"os"
	"os/signal"
	"time"
	"strconv"
	"syscall"
	"unsafe"


	"github.com/christophwitzko/flight-booking-service/pkg/database"
	"github.com/christophwitzko/flight-booking-service/pkg/database/seeder"
	"github.com/christophwitzko/flight-booking-service/pkg/logger"
	"github.com/christophwitzko/flight-booking-service/pkg/service"
)

func SetCPUAffinity(cpu int) error {
	var mask [1024 / 64]uint64
	mask[cpu/64] = 1 << (cpu % 64)

	_, _, errno := syscall.RawSyscall(
		syscall.SYS_SCHED_SETAFFINITY,
		0,
		uintptr(len(mask)*8),
		uintptr(unsafe.Pointer(&mask[0])),
	)

	if errno != 0 {
		return errno
	}
	return nil
}

func main() {
	// Get CPU core from environment variable, default to core 0
	cpuCore := 0
	if coreStr := os.Getenv("CPU_CORE"); coreStr != "" {
		if core, err := strconv.Atoi(coreStr); err == nil {
			cpuCore = core
		}
	}

	// Set CPU affinity based on CPU_CORE
	if err := SetCPUAffinity(cpuCore); err != nil {
		panic("failed to set CPU affinity: " + err.Error())
	}


	level := logger.DebugLevel
	levelName := os.Getenv("LOG_LEVEL")
	switch levelName {
	case "debug":
		level = logger.DebugLevel
	case "info":
		level = logger.InfoLevel
	case "warn":
		level = logger.WarnLevel
	case "error":
		level = logger.ErrorLevel
	}
	log := logger.New(level)
	if levelName != "" {
		log.Infof("log level: %s", levelName)
	}
	if err := run(log); err != nil {
		log.Fatal(err)
	}
}

func getBindAddress() (string, error) {
	// Environment variables for addresses
	primaryPort := os.Getenv("PORT1")
	secondaryPort := os.Getenv("PORT2")

	if primaryPort == "" {
		primaryPort = "3000"
	}
	if secondaryPort == "" {
		secondaryPort = "3001"
	}

	// Function to check if a port is available
	isPortAvailable := func(port string) bool {
		ln, err := net.Listen("tcp", ":"+port)
		if err != nil {
			return false
		}
		ln.Close() // Close the listener immediately if the port is free
		return true
	}

	if isPortAvailable(primaryPort) {
		return "0.0.0.0:" + primaryPort, nil
	} else if isPortAvailable(secondaryPort) {
		return "0.0.0.0:" + secondaryPort, nil
	} else {
		return "", errors.New("both primary and secondary ports are unavailable")
	}
}


func run(log *logger.Logger) error {
	db, err := database.New()
	if err != nil {
		return err
	}
	err = seeder.Seed(db, 1000)
	if err != nil {
		return err
	}

	s := service.New(log, db)
	s.Auth["user"] = "pw"

	// Capture both address and error from getBindAddress()
	addr, err := getBindAddress()
	if err != nil {
		return err // Handle error if no available address
	}

	srv := &http.Server{
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 60 * time.Second,
		IdleTimeout:  60 * time.Second,
		Addr:         addr, // Use the obtained address
		Handler:      s,
	}

	listenErrCh := make(chan error)
	go func() {
		log.Infof("listening on %s", srv.Addr)
		sErr := srv.ListenAndServe()
		if !errors.Is(sErr, http.ErrServerClosed) {
			listenErrCh <- sErr
		}
		close(listenErrCh)
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	select {
	case <-ctx.Done():
		log.Info("shutting down...")
	case err = <-listenErrCh:
		log.Errorf("error listening on %s: %s", srv.Addr, err)
	}
	stop()

	log.Info("stopping server...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err = srv.Shutdown(ctx); errors.Is(err, context.DeadlineExceeded) {
		log.Info("closing server...")
		if err = srv.Close(); err != nil {
			log.Error(err)
		}
		<-time.After(time.Second)
	} else if err != nil {
		log.Error(err)
	}

	log.Info("closing database...")
	return db.Close()
}

