package main

import (
	"bufio"
	"log"
	"os"
	"strings"
	"time"
)

func main() {
	timeStart := time.Now()
	readFile, err := os.Open("shit2.csv")
	if err != nil {
		log.Println(err)
	}
	writeFile, err := os.Create("shit3.csv")
	if err != nil {
		log.Println(err)
	}
	fileScanner := bufio.NewScanner(readFile)
	fileScanner.Split(bufio.ScanLines)
	w := bufio.NewWriter(writeFile)

	lineNumber := 1
	limit := 100_000_000
	numberOfColumns := 0
	numberOfViolatingLines := 0
	for fileScanner.Scan() {
		if lineNumber == limit+1 {
			break
		}
		line := fileScanner.Text()
		lineArr := strings.Split(line, "$")
		if lineNumber == 1 {
			numberOfColumns = len(lineArr)
		}
		if len(lineArr) != numberOfColumns {
			// log.Printf("number of values %d in line %d does not match header\n", len(lineArr), lineNumber)
			// fmt.Println(line)
			numberOfViolatingLines++
		} else {
			w.WriteString(line + "\n")
		}
		lineNumber++
	}
	readFile.Close()
	w.Flush()

	timeElapsed := time.Since(timeStart)
	log.Printf(`REPORT:
Number of columns in header: %d
Total number of lines: %d
Number of violating lines: %d
Execution time: %s
`, numberOfColumns, lineNumber-1, numberOfViolatingLines, timeElapsed)
}
