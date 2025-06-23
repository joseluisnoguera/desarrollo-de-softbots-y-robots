package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

// Item represents an item in the supermarket
type Item struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Price    int    `json:"price"`
	Quantity int    `json:"quantity"`
	MaxStock int    `json:"max_stock"`
}

type UpdateItemQuantityRequest struct {
	ID       int `json:"id"`
	Quantity int `json:"quantity"`
}

var db *sql.DB

const itemsPath = "/items"

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./supermarket.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable()
	seedData()

	r := mux.NewRouter()
	r.HandleFunc(itemsPath, getItems).Methods("GET")
	r.HandleFunc(itemsPath, buyItem).Methods("POST")
	r.HandleFunc(itemsPath, restockItem).Methods("PUT")

	log.Println("Server starting on port 3005...")
	log.Fatal(http.ListenAndServe(":3005", r))
}

func createTable() {
	statement, err := db.Prepare(`
		CREATE TABLE IF NOT EXISTS items (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT UNIQUE,
			price INTEGER,
			quantity INTEGER,
			max_stock INTEGER
		)
	`)
	if err != nil {
		log.Fatal(err)
	}
	statement.Exec()
}

func seedData() {
	// Check if items already exist
	rows, err := db.Query("SELECT name FROM items")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	if rows.Next() {
		// Data already seeded
		return
	}

	items := []Item{
		{Name: "manzanas", Price: 150, Quantity: 20, MaxStock: 100},
		{Name: "platanos", Price: 100, Quantity: 30, MaxStock: 100},
		{Name: "leche", Price: 200, Quantity: 15, MaxStock: 50},
		{Name: "pan", Price: 120, Quantity: 25, MaxStock: 60},
		{Name: "huevos", Price: 250, Quantity: 40, MaxStock: 80},
		{Name: "queso", Price: 300, Quantity: 10, MaxStock: 40},
		{Name: "jamón", Price: 400, Quantity: 12, MaxStock: 30},
		{Name: "jugo de naranja", Price: 180, Quantity: 18, MaxStock: 50},
	}

	tx, err := db.Begin()
	if err != nil {
		log.Fatal(err)
	}

	stmt, err := tx.Prepare("INSERT INTO items (name, price, quantity, max_stock) VALUES (?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmt.Close()

	for _, item := range items {
		_, err := stmt.Exec(item.Name, item.Price, item.Quantity, item.MaxStock)
		if err != nil {
			log.Fatal(err)
		}
	}
	tx.Commit()
}

func getItems(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, name, price, quantity, max_stock FROM items")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []Item
	for rows.Next() {
		var item Item
		if err := rows.Scan(&item.ID, &item.Name, &item.Price, &item.Quantity, &item.MaxStock); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(items)
}

func buyItem(w http.ResponseWriter, r *http.Request) {
	var reqs []UpdateItemQuantityRequest
	if err := json.NewDecoder(r.Body).Decode(&reqs); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	tx, err := db.Begin()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer tx.Rollback() // Rollback on any error return

	for _, req := range reqs {
		if req.Quantity <= 0 {
			http.Error(w, "Quantity must be positive for all items", http.StatusBadRequest)
			return
		}

		result, err := tx.Exec("UPDATE items SET quantity = quantity - ? WHERE id = ? AND quantity >= ?", req.Quantity, req.ID, req.Quantity)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		rowsAffected, err := result.RowsAffected()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		if rowsAffected == 0 {
			http.Error(w, "Item not found or not enough stock for item with id "+strconv.Itoa(req.ID), http.StatusBadRequest)
			return
		}
	}

	if err := tx.Commit(); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func restockItem(w http.ResponseWriter, r *http.Request) {
	var reqs []UpdateItemQuantityRequest
	if err := json.NewDecoder(r.Body).Decode(&reqs); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	tx, err := db.Begin()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer tx.Rollback()

	for _, req := range reqs {
		if req.Quantity <= 0 {
			http.Error(w, "Quantity must be positive for all items", http.StatusBadRequest)
			return
		}

		var currentQuantity, maxStock int
		err := tx.QueryRow("SELECT quantity, max_stock FROM items WHERE id = ?", req.ID).Scan(&currentQuantity, &maxStock)
		if err != nil {
			if err == sql.ErrNoRows {
				http.Error(w, "Item not found with id "+strconv.Itoa(req.ID), http.StatusNotFound)
			} else {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}
			return
		}

		if currentQuantity+req.Quantity > maxStock {
			http.Error(w, "Restock quantity exceeds maximum stock for item with id "+strconv.Itoa(req.ID), http.StatusBadRequest)
			return
		}

		_, err = tx.Exec("UPDATE items SET quantity = quantity + ? WHERE id = ?", req.Quantity, req.ID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	if err := tx.Commit(); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}
