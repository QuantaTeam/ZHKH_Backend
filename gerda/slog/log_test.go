package slog_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/slog"
)

func TestDev(t *testing.T) {
	_, err := slog.Dev()
	require.NoError(t, err)
}

func TestProd(t *testing.T) {
	_, err := slog.Prod()
	require.NoError(t, err)
}
