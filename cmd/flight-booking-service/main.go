package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/christophwitzko/flight-booking-service/pkg/database"
	"github.com/christophwitzko/flight-booking-service/pkg/database/seeder"
	"github.com/christophwitzko/flight-booking-service/pkg/logger"
	"github.com/christophwitzko/flight-booking-service/pkg/service"
)

// SetCPUAffinity sets the CPU affinity for the current process.
/*func SetCPUAffinity(cpu int) error {
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
*/
func main() {
	// Define command-line flags for CPU core and port
	//cpuCore := flag.Int("cpuCore", 0, "CPU core to bind the program to")
	port := flag.Int("port", 3000, "Port for the HTTP server")
	flag.Parse()

	/*
	// Set CPU affinity based on the provided core
	if err := SetCPUAffinity(*cpuCore); err != nil {
		panic("failed to set CPU affinity: " + err.Error())
	}

	*/

	// Set the address using the provided port
	addr := fmt.Sprintf("0.0.0.0:%d", *port)

	// Start the application
	if err := run(addr); err != nil {
		panic(err)
	}
}

func run(addr string) error {
	log := logger.New(logger.InfoLevel)

	db, err := database.New()
	if err != nil {
		return err
	}
	defer db.Close()

	err = seeder.Seed(db, 1000)
	if err != nil {
		return err
	}

	s := service.New(log, db)
	s.Auth["user"] = "pw"

	srv := &http.Server{
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 60 * time.Second,
		IdleTimeout:  60 * time.Second,
		Addr:         addr,
		Handler:      s,
	}

	listenErrCh := make(chan error)
	go func() {
		log.Infof("Listening on %s", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			listenErrCh <- err
		}
		close(listenErrCh)
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	select {
	case <-ctx.Done():
		log.Info("Shutting down server...")
	case err := <-listenErrCh:
		log.Errorf("Server error: %s", err)
		return err
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return srv.Shutdown(shutdownCtx)
}
