package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/caarlos0/env/v6"
	"github.com/jmoiron/sqlx"
	"github.com/schollz/progressbar/v3"
)

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
			Coordinates [][][]interface{} `json:"coordinates"`
			Type        string            `json:"type,omitempty"`
		} `json:"geoData"`
	} `json:"Cells"`
}

type GeoObject struct {
	ID int64
	// ADDRESS
	Adress string
	// SIMPLE_ADDRESS
	ShortAdress string
	X           float64
	Y           float64
}

type PGConnectionData struct {
	DB       string `env:"POSTGRES_DB"`
	Password string `env:"POSTGRES_PASSWORD"`
	User     string `env:"POSTGRES_USER"`
	Host     string `env:"POSTGRES_SERVER"`
}

func OpenDB() (*sqlx.DB, error) {
	cfg := PGConnectionData{}
	err := env.Parse(&cfg)
	if err != nil {
		return &sqlx.DB{}, err
	}

	db, err := sqlx.Connect(
		"postgres",
		fmt.Sprintf(
			"postgres://%s:%s@%s:5432/%s?sslmode=disable",
			cfg.User,
			cfg.Password,
			cfg.Host,
			cfg.DB,
		),
	)
	return db, err
}

func readRespBody(resp *http.Response) []byte {
	defer resp.Body.Close()
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Panicf("failed to read response body: %s\n", err)
	}
	return responseBody
}

func main() {
	// db, err := OpenDB()
	// if err != nil {
	// 	log.Panicf("could not open pg connection\n")
	// }
	client := &http.Client{
		Timeout: 200 * time.Second,
	}
	f, err := os.OpenFile("mosru.csv", os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0o600)
	if err != nil {
		panic(err)
	}

	bar := progressbar.Default(475401)
	step := 1000
	for skip := 0; skip < 475401; skip += step {
		bar.Add(step)
		req, err := http.NewRequest(http.MethodGet, "https://apidata.mos.ru/v1/datasets/60562/rows", nil)
		if err != nil {
			log.Panicf("failed to construct external request for geocoding: %s\n", err)
		}
		q := req.URL.Query()
		q.Add("api_key", "8d93424e7aa505db6c542451500d8f34")
		q.Add("$top", fmt.Sprintf("%d", step))
		q.Add("$skip", fmt.Sprintf("%d", skip))

		var resp *http.Response
		req.URL.RawQuery = q.Encode()
		for i := 0; i < 10; i++ {
			if i == 9 {
				log.Panicf("failed to send 10 times, exiting")
			}
			resp, err = client.Do(req)
			if err != nil {
				log.Println("errored when sending request to the server, retrying")
				continue
			}
			if resp.StatusCode == 200 {
				break
			} else {
				log.Printf("geocode non 200 response code: %d, retrying\n", resp.StatusCode)
				continue
			}
		}
		responseBody := readRespBody(resp)
		var respStruct MosRuDataResp
		err = json.Unmarshal(responseBody, &respStruct)
		if err != nil {
			log.Panicf("failed to unmarshal json struct; skip: %d: %s\n", skip, err)
		}
		if len(respStruct) == 0 {
			log.Println("0 length response")
			return
		}
		for _, object := range respStruct {
			id := object.GlobalID
			address := object.Cells.Address
			short_address := object.Cells.SimpleAddress
			coordinatesInterOne := object.Cells.GeoData.Coordinates
			if len(coordinatesInterOne) == 0 {
				log.Println("skipped one object, coordinatesInterOne has 0 length")
				continue
			}
			coordinatesInterTwo := coordinatesInterOne[0]
			if len(coordinatesInterTwo) == 0 {
				log.Println("skipped one object, coordinatesInterTwo has 0 length")
				continue
			}
			coordinatesInter := coordinatesInterTwo[0]
			if len(coordinatesInter) == 0 {
				log.Println("skipped one object, coordinatesInter has 0 length")
				continue
			}
			x := 0.0
			y := 0.0

			y, ok := coordinatesInter[0].(float64)
			if ok {
				x, _ = coordinatesInter[1].(float64)
			} else {
				extra, okExtra := coordinatesInter[0].([]interface{})
				if okExtra {
					y = extra[0].(float64)
					x = extra[1].(float64)
				}
			}

			csvLine := fmt.Sprintf("%d$%s$%s$%f$%f\n", id, address, short_address, x, y)
			if _, err = f.WriteString(csvLine); err != nil {
				panic(err)
			}
		}
        log.Printf("skip %d done\n", skip)
	}
}
