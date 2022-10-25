package config

import (
	"fmt"

	"github.com/caarlos0/env/v6"
)

const prefix = ""

type Config struct {
	Secret          string `env:"SECRET" envDefault:"12345"`
	YandexGeoAPIKey string `env:"YANDEX_GEOCODER_API_KEY,required"`
}

func Read() (*Config, error) {
	cfg := Config{}
	if err := env.Parse(&cfg, env.Options{
		Prefix: prefix,
	}); err != nil {
		return nil, fmt.Errorf("failed to parse config from env vars: %w", err)
	}

	return &cfg, nil
}
