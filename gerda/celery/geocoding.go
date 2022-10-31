package celery

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	"go.uber.org/zap"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/config"
)

type YandexGeoCodeResp struct {
	Response struct {
		GeoObjectCollection struct {
			MetaDataProperty struct {
				GeocoderResponseMetaData struct {
					Request string `json:"request,omitempty"`
					Results string `json:"results,omitempty"`
					Found   string `json:"found,omitempty"`
				} `json:"GeocoderResponseMetaData,omitempty"`
			} `json:"metaDataProperty,omitempty"`
			FeatureMember []struct {
				GeoObject struct {
					MetaDataProperty struct {
						GeocoderMetaData struct {
							Precision string `json:"precision,omitempty"`
							Text      string `json:"text,omitempty"`
							Kind      string `json:"kind,omitempty"`
							Address   struct {
								CountryCode string `json:"country_code,omitempty"`
								Formatted   string `json:"formatted,omitempty"`
								PostalCode  string `json:"postal_code,omitempty"`
								Components  []struct {
									Kind string `json:"kind,omitempty"`
									Name string `json:"name,omitempty"`
								} `json:"Components,omitempty"`
							} `json:"Address,omitempty"`
							AddressDetails struct {
								Country struct {
									AddressLine        string `json:"AddressLine,omitempty"`
									CountryNameCode    string `json:"CountryNameCode,omitempty"`
									CountryName        string `json:"CountryName,omitempty"`
									AdministrativeArea struct {
										AdministrativeAreaName string `json:"AdministrativeAreaName,omitempty"`
										Locality               struct {
											LocalityName string `json:"LocalityName,omitempty"`
											Thoroughfare struct {
												ThoroughfareName string `json:"ThoroughfareName,omitempty"`
												Premise          struct {
													PremiseNumber string `json:"PremiseNumber,omitempty"`
													PostalCode    struct {
														PostalCodeNumber string `json:"PostalCodeNumber,omitempty"`
													} `json:"PostalCode,omitempty"`
												} `json:"Premise,omitempty"`
											} `json:"Thoroughfare,omitempty"`
										} `json:"Locality,omitempty"`
									} `json:"AdministrativeArea,omitempty"`
								} `json:"Country,omitempty"`
							} `json:"AddressDetails,omitempty"`
						} `json:"GeocoderMetaData,omitempty"`
					} `json:"metaDataProperty,omitempty"`
					Name        string `json:"name,omitempty"`
					Description string `json:"description,omitempty"`
					BoundedBy   struct {
						Envelope struct {
							LowerCorner string `json:"lowerCorner,omitempty"`
							UpperCorner string `json:"upperCorner,omitempty"`
						} `json:"Envelope,omitempty"`
					} `json:"boundedBy,omitempty"`
					Point struct {
						Pos string `json:"pos,omitempty"`
					} `json:"Point,omitempty"`
				} `json:"GeoObject,omitempty"`
			} `json:"featureMember,omitempty"`
		} `json:"GeoObjectCollection,omitempty"`
	} `json:"response,omitempty"`
}

type MosRuDataResp []struct {
	GlobalID int `json:"global_id,omitempty"`
	Number   int `json:"Number,omitempty"`
	Cells    struct {
		GlobalID            int         `json:"global_id,omitempty"`
		ObjType             string      `json:"OBJ_TYPE,omitempty"`
		OnTerritoryOfMoscow string      `json:"OnTerritoryOfMoscow,omitempty"`
		Address             string      `json:"ADDRESS,omitempty"`
		SimpleAddress       string      `json:"SIMPLE_ADDRESS,omitempty"`
		Unom                int         `json:"UNOM,omitempty"`
		P0                  interface{} `json:"P0,omitempty"`
		P1                  string      `json:"P1,omitempty"`
		P2                  string      `json:"P2,omitempty"`
		P3                  interface{} `json:"P3,omitempty"`
		P4                  interface{} `json:"P4,omitempty"`
		P5                  string      `json:"P5,omitempty"`
		P6                  interface{} `json:"P6,omitempty"`
		P7                  string      `json:"P7,omitempty"`
		P90                 interface{} `json:"P90,omitempty"`
		P91                 interface{} `json:"P91,omitempty"`
		L1Type              string      `json:"L1_TYPE,omitempty"`
		L1Value             string      `json:"L1_VALUE,omitempty"`
		L2Type              string      `json:"L2_TYPE,omitempty"`
		L2Value             string      `json:"L2_VALUE,omitempty"`
		L3Type              interface{} `json:"L3_TYPE,omitempty"`
		L3Value             string      `json:"L3_VALUE,omitempty"`
		L4Type              interface{} `json:"L4_TYPE,omitempty"`
		L4Value             string      `json:"L4_VALUE,omitempty"`
		L5Type              interface{} `json:"L5_TYPE,omitempty"`
		L5Value             string      `json:"L5_VALUE,omitempty"`
		AdmArea             string      `json:"ADM_AREA,omitempty"`
		District            string      `json:"DISTRICT,omitempty"`
		Nreg                int         `json:"NREG,omitempty"`
		Dreg                string      `json:"DREG,omitempty"`
		NFias               string      `json:"N_FIAS,omitempty"`
		DFias               string      `json:"D_FIAS,omitempty"`
		KadN                []struct {
			KadN string `json:"KAD_N,omitempty"`
		} `json:"KAD_N,omitempty"`
		KadZu   []interface{} `json:"KAD_ZU,omitempty"`
		Kladr   string        `json:"KLADR,omitempty"`
		Tdoc    string        `json:"TDOC,omitempty"`
		Ndoc    string        `json:"NDOC,omitempty"`
		Ddoc    string        `json:"DDOC,omitempty"`
		AdrType string        `json:"ADR_TYPE,omitempty"`
		Vid     string        `json:"VID,omitempty"`
		Sostad  string        `json:"SOSTAD,omitempty"`
		Status  string        `json:"STATUS,omitempty"`
		GeoData struct {
			Coordinates [][][]float64 `json:"coordinates"`
			Type        string        `json:"type,omitempty"`
		} `json:"geoData"`
	} `json:"Cells"`
}

type ApplicationGeo struct {
	ID             int64          `db:"id"`
	Adress         string         `db:"Адрес проблемы"`
	GeoCoordinates sql.NullString `db:"geo_coordinates"`
}

func readRespBody(resp *http.Response, logger *zap.Logger) ([]byte, bool) {
	defer resp.Body.Close()
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		logger.Error("failed to read response body", zap.Error(err))
		return nil, false
	}
	return responseBody, true
}

// $.response.[0].GeoObject.Point.pos
func geocode(logger *zap.Logger, rdb *sqlx.DB, conf *config.Config, period time.Duration) {
	ticker := time.NewTicker(period)
	applicationsWithoutGeo := make([]ApplicationGeo, 0)
	for range ticker.C {
		if !conf.GeocodeTaskEnabled {
			logger.Warn("geocode task disabled, skipping")
			continue
		}
		query := fmt.Sprintf(`--sql
            select application.id, application."Адрес проблемы", application.geo_coordinates from application
            where application.geo_coordinates is NULL
            limit %d`, conf.SimultaneousGeocodeUpdates)
		if err := rdb.Select(&applicationsWithoutGeo, query); err != nil {
			logger.Error("could not get project from db", zap.Error(err))
			continue
		}
		if len(applicationsWithoutGeo) == 0 {
			logger.Info("all applications are already geocoded, exiting")
			continue
		}

		client := &http.Client{
			Timeout: 50 * time.Second,
		}
		for _, application := range applicationsWithoutGeo {
			req, err := http.NewRequest(http.MethodGet, "https://apidata.mos.ru/v1/datasets/60562/rows", nil)
			if err != nil {
				logger.Error("failed to construct external request for geocoding", zap.Error(err))
				continue
			}
			q := req.URL.Query()
			q.Add("api_key", conf.MOS_RU_OPEN_DATA_API_KEY)
			filter := fmt.Sprintf("Cells/SIMPLE_ADDRESS eq '%s'", application.Adress)
			q.Add("$filter", filter)
			q.Add("$top", "1")
			req.URL.RawQuery = q.Encode()
			resp, err := client.Do(req)
			if err != nil {
				logger.Info("Errored when sending request to the server")
				continue
			}
			responseBody, ok := readRespBody(resp, logger)
			if !ok {
				continue
			}

			if resp.StatusCode != 200 {
				logger.Error("geocode non 200 response code", zap.Int("code", resp.StatusCode))
				continue
			}
			var respStruct MosRuDataResp
			err = json.Unmarshal(responseBody, &respStruct)
			if err != nil {
				logger.Error("failed to unmarshal json", zap.Error(err))
				continue
			}
			if len(respStruct) == 0 {
				logger.Error("geocoding: resp body is empty", zap.Error(err))
				continue
			}
			coordinates := respStruct[0].Cells.GeoData.Coordinates[0][0]
			coordinatesFloats := make([]float64, 2)
			coordinatesFloats[0] = coordinates[1]
			coordinatesFloats[1] = coordinates[0]

			logger.Info("opening tx for geocoding", zap.Int("number", len(applicationsWithoutGeo)))
			tx, err := rdb.Begin()
			if err != nil {
				logger.Error("failed to create db transaction", zap.Error(err))
				continue
			}
			update := "update application set geo_coordinates = $1 where application.id = $2"
			if _, err = tx.Exec(update, pq.Array(coordinatesFloats), application.ID); err != nil {
				logger.Error("failed to update geo coordinates", zap.Error(err))
				if e := tx.Rollback(); e != nil {
					logger.Error("failed to rollback transaction", zap.Error(err))
				}
				continue
			}
			if err := tx.Commit(); err != nil {
				logger.Error("failed to commit tx", zap.Error(err))
				continue
			}
			logger.Info("One update of coordinates successful", zap.Int64("application_id", application.ID))
		}

	}
}
