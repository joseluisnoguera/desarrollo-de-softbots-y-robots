package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"supermarket-api/pkg/types"
)

const (
	apiURL    = "http://localhost:3005"
	itemsPath = "/items"
)

func ListItems() (string, error) {
	resp, err := http.Get(apiURL + itemsPath)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func BuyItems(items []types.UpdateItemQuantityRequest) (string, error) {
	jsonBody, err := json.Marshal(items)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", apiURL+itemsPath, bytes.NewBuffer(jsonBody))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to buy items: %s", string(body))
	}

	return "Items purchased successfully", nil
}

func RestockItems(items []types.UpdateItemQuantityRequest) (string, error) {
	jsonBody, err := json.Marshal(items)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("PUT", apiURL+itemsPath, bytes.NewBuffer(jsonBody))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to restock items: %s", string(body))
	}

	return "Items restocked successfully", nil
}
