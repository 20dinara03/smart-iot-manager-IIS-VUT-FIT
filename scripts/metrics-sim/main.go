package main

import (
	"encoding/json"
	"fmt"
	"github.com/nats-io/nats.go"
	"gopkg.in/yaml.v3"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	configFile  = "config.yaml"
	NATSHeader  = "X-Device-ID"
	NATSSubject = "metric"
)

type Attribute struct {
	Name     string `yaml:"name"`
	MinValue int    `yaml:"minVal"`
	MaxValue int    `yaml:"maxVal"`
}

type DeviceConfig struct {
	Id    string      `yaml:"id"`
	Attrs []Attribute `yaml:"attrs"`
}

type Config struct {
	Devices []DeviceConfig `yaml:"devices"`
	Server  string         `yaml:"server"`
}

var (
	stopMain      = make(chan os.Signal, 1)
	goroutineStop = make(chan os.Signal, 1)
)

func main() {
	filename := configFile
	if len(os.Args) == 2 {
		// get filename
		filename = os.Args[1]
	}

	// read config file
	config, err := readConfig(filename)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	// connect to NATS server
	server, err := nats.Connect(config.Server)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	// start device simulators
	for _, d := range config.Devices {
		go sendMetrics(d, server)
	}

	// wait for signal
	signal.Notify(stopMain, syscall.SIGTERM, syscall.SIGINT, syscall.SIGKILL)
	<-stopMain

	// stop daemons
	for range config.Devices {
		goroutineStop <- syscall.SIGTERM
	}
}

func readConfig(filename string) (*Config, error) {
	data, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer data.Close()

	var config Config
	err = yaml.NewDecoder(data).Decode(&config)

	if err != nil {
		return nil, err
	}

	return &config, nil
}

func sendMetrics(d DeviceConfig, server *nats.Conn) {
LOOP:
	for {
		select {
		case <-goroutineStop:
			break LOOP
		default:
			msg := nats.NewMsg(NATSSubject)
			msg.Header.Add(NATSHeader, d.Id)
			msg.Header.Add("username", "broker")
			msg.Header.Add("password", "pass")

			var bodyMap = make(map[string]int)

			for _, a := range d.Attrs {
				fmt.Println(a.Name, a.MinValue, a.MaxValue)
				bodyMap[a.Name] = random(a.MaxValue, a.MinValue)
			}

			var err error
			msg.Data, err = json.Marshal(bodyMap)
			if err != nil {
				fmt.Println(err)
				continue
			}

			err = server.PublishMsg(msg)

			time.Sleep(3 * time.Second)
		}
	}
}

func random(max, min int) int {
	return rand.Intn(max-min) + min
}
