package main

import (
	"fmt"

	"supermarket-api/pkg/client"
	"supermarket-api/pkg/types"

	mcp "github.com/metoro-io/mcp-golang"
	"github.com/metoro-io/mcp-golang/transport/stdio"
)

type BuyItemsArguments struct {
	Items []types.UpdateItemQuantityRequest `json:"items" jsonschema:"required,description=The items to be bought"`
}

type ListItemsArguments struct{}

type RestockItemsArguments struct {
	Items []types.UpdateItemQuantityRequest `json:"items" jsonschema:"required,description=The items to be restocked"`
}

func main() {
	done := make(chan struct{})

	server := mcp.NewServer(stdio.NewStdioServerTransport())

	err := server.RegisterTool("list_items", "List all items in the supermarket", func(arguments ListItemsArguments) (*mcp.ToolResponse, error) {
		items, err := client.ListItems()
		if err != nil {
			return nil, err
		}
		return mcp.NewToolResponse(mcp.NewTextContent(items)), nil
	})
	if err != nil {
		panic(err)
	}

	err = server.RegisterTool("buy_items", "Buy items from the supermarket", func(arguments BuyItemsArguments) (*mcp.ToolResponse, error) {
		result, err := client.BuyItems(arguments.Items)
		if err != nil {
			return nil, err
		}
		return mcp.NewToolResponse(mcp.NewTextContent(result)), nil
	})
	if err != nil {
		panic(err)
	}

	err = server.RegisterTool("restock_items", "Restock items in the supermarket", func(arguments RestockItemsArguments) (*mcp.ToolResponse, error) {
		result, err := client.RestockItems(arguments.Items)
		if err != nil {
			return nil, err
		}
		return mcp.NewToolResponse(mcp.NewTextContent(result)), nil
	})
	if err != nil {
		panic(err)
	}

	fmt.Println("MCP Server for Supermarket API is running...")
	err = server.Serve()
	if err != nil {
		panic(err)
	}

	<-done
}
