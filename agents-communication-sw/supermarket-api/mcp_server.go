package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
)

// MCPRequest represents the request from the agent.
type MCPRequest struct {
	Prompt string `json:"prompt"`
}

// MCPResponse represents the response to the agent.
type MCPResponse struct {
	Content string `json:"content"`
}

// mcpHandler handles requests to the MCP server.
func mcpHandler(w http.ResponseWriter, r *http.Request) {
	var req MCPRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Simple command parsing from the prompt.
	parts := strings.Fields(req.Prompt)
	if len(parts) == 0 {
		http.Error(w, "Empty prompt", http.StatusBadRequest)
		return
	}

	command := parts[0]
	args := parts[1:]

	var responseContent string
	var err error

	switch command {
	case "list_items":
		responseContent, err = mcpListItems()
	case "buy_items":
		items, parseErr := mcpParseItems(args)
		if parseErr != nil {
			err = parseErr
		} else {
			responseContent, err = mcpBuyItems(items)
		}
	case "restock_items":
		items, parseErr := mcpParseItems(args)
		if parseErr != nil {
			err = parseErr
		} else {
			responseContent, err = mcpRestockItems(items)
		}
	default:
		responseContent = "Unknown command: " + command
	}

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	resp := MCPResponse{Content: responseContent}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func mcpParseItems(args []string) ([]UpdateItemQuantityRequest, error) {
	var items []UpdateItemQuantityRequest
	for _, arg := range args {
		parts := strings.Split(arg, ",")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid item format: %s. Expected id,quantity", arg)
		}
		id, err := strconv.Atoi(parts[0])
		if err != nil {
			return nil, fmt.Errorf("invalid item id: %s", parts[0])
		}
		quantity, err := strconv.Atoi(parts[1])
		if err != nil {
			return nil, fmt.Errorf("invalid item quantity: %s", parts[1])
		}
		items = append(items, UpdateItemQuantityRequest{ID: id, Quantity: quantity})
	}
	return items, nil
}

const mcpApiURL = "http://localhost:3005"

func mcpListItems() (string, error) {
	resp, err := http.Get(mcpApiURL + "/items")
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func mcpBuyItems(items []UpdateItemQuantityRequest) (string, error) {
	jsonBody, err := json.Marshal(items)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", mcpApiURL+"/items", bytes.NewBuffer(jsonBody))
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
		body, _ := ioutil.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to buy items: %s", string(body))
	}

	return "Items purchased successfully", nil
}

func mcpRestockItems(items []UpdateItemQuantityRequest) (string, error) {
	jsonBody, err := json.Marshal(items)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("PUT", mcpApiURL+"/items", bytes.NewBuffer(jsonBody))
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
		body, _ := ioutil.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to restock items: %s", string(body))
	}

	return "Items restocked successfully", nil
}
