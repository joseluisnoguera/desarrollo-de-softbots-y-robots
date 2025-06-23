package types

// Item represents an item in the supermarket
type Item struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Price    int    `json:"price"`
	Quantity int    `json:"quantity"`
	MaxStock int    `json:"max_stock"`
}

// UpdateItemQuantityRequest represents the request to update the quantity of an item.
type UpdateItemQuantityRequest struct {
	ID       int `json:"id"`
	Quantity int `json:"quantity"`
}
