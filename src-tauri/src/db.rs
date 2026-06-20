use serde::{Serialize, Deserialize};
use rusqlite::{params, Connection, Result};
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Product {
    pub id: Option<i64>,
    pub sku: String,
    pub name: String,
    pub category: String,
    pub stock_quantity: f64,
    pub reorder_level: f64,
    pub cost_price: f64,
    pub selling_price: f64,
    pub image_path: Option<String>,
    pub supplier_id: Option<i64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Contact {
    pub id: Option<i64>,
    pub name: String,
    pub phone: String,
    pub email: Option<String>,
    pub contact_type: String, // "Customer" or "Supplier"
    pub balance: f64,          // Net Khata Balance: Positive means we owe them, negative means they owe us
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Transaction {
    pub id: Option<i64>,
    pub contact_id: i64,
    pub amount: f64,           // Amount in PKR
    pub flow_type: String,     // "Cash In" (Payment received), "Cash Out" (Payment paid), "Credit" (Udhaar given), "Debit" (Purchased on credit)
    pub description: String,
    pub timestamp: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PriceHistoryEntry {
    pub id: Option<i64>,
    pub product_id: i64,
    pub change_date: String,
    pub old_price: f64,
    pub new_price: f64,
}

pub struct DbManager {
    db_path: PathBuf,
}

impl DbManager {
    pub fn new(app_data_dir: PathBuf) -> Self {
        std::fs::create_dir_all(&app_data_dir).ok();
        let db_path = app_data_dir.join("hardware_shop.db");
        let conn = Connection::open(&db_path).expect("Failed to open SQLite database");
        
        // Create tables
        conn.execute(
            "CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                contact_type TEXT NOT NULL,
                balance REAL DEFAULT 0.0
            )",
            [],
        ).unwrap();

        conn.execute(
            "CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                stock_quantity REAL NOT NULL,
                reorder_level REAL NOT NULL,
                cost_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                image_path TEXT,
                supplier_id INTEGER,
                FOREIGN KEY(supplier_id) REFERENCES contacts(id)
            )",
            [],
        ).unwrap();

        conn.execute(
            "CREATE TABLE IF NOT EXISTS khata_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                flow_type TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )",
            [],
        ).unwrap();

        conn.execute(
            "CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                change_date TEXT NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )",
            [],
        ).unwrap();

        let mut mgr = DbManager { db_path };
        mgr.seed_data_if_empty().ok();
        mgr
    }

    fn get_conn(&self) -> Result<Connection> {
        Connection::open(&self.db_path)
    }

    fn seed_data_if_empty(&mut self) -> Result<()> {
        let conn = self.get_conn()?;
        
        // Check if seeded already
        let count: i64 = conn.query_row("SELECT count(*) FROM contacts", [], |r| r.get(0))?;
        if count > 0 {
            return Ok(());
        }

        // Seed Suppliers and Customers (Grahak) with explicit IDs
        conn.execute(
            "INSERT INTO contacts (id, name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
            params![1, "Walk-in Grahak", "0000-0000000", None::<String>, "Customer", 0.0],
        )?;
        conn.execute(
            "INSERT INTO contacts (id, name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
            params![2, "Kamran Bhai", "0300-1234567", "kamran@gmail.com", "Customer", -2500.0], // owes us Rs. 2500
        )?;
        conn.execute(
            "INSERT INTO contacts (id, name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
            params![3, "Zahid Electric Store", "0321-7654321", "zahid@electric.com", "Supplier", 12000.0], // we owe them Rs. 12,000
        )?;
        conn.execute(
            "INSERT INTO contacts (id, name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
            params![4, "Siddique Pipe Works", "0333-1122334", "siddique@pipes.com", "Supplier", 0.0],
        )?;
        conn.execute(
            "INSERT INTO contacts (id, name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
            params![5, "Farhan Painter", "0345-9988776", "farhan@paint.com", "Customer", 0.0],
        )?;

        // Seed Products referencing correct Supplier IDs (Paint -> 3, Electrical -> 3, Plumbing -> 4, Fasteners -> 2)
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-001", "G.I. Pipe 1\" (Tariq Pipe)", "Plumbing", 120.0, 30.0, 380.0, 450.0, None::<String>, 4],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-002", "PVC Pipe 3\" (Beta Pipes)", "Plumbing", 80.0, 20.0, 310.0, 380.0, None::<String>, 4],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-003", "Fast Cables 3/29 Single Core", "Electrical", 15.0, 5.0, 7800.0, 8500.0, None::<String>, 3],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-004", "Fast Cables 7/29 Single Core", "Electrical", 8.0, 3.0, 13200.0, 14500.0, None::<String>, 3],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-005", "Millat Ceiling Fan 56\"", "Electrical", 25.0, 5.0, 8600.0, 9500.0, None::<String>, 3],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-006", "Berger Robbialac Matte White 1L", "Paint", 45.0, 10.0, 1950.0, 2400.0, None::<String>, 2],
        )?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params!["SKU-007", "Steel Screw 1.5\" (Box)", "Fasteners", 50.0, 15.0, 320.0, 420.0, None::<String>, 2],
        )?;

        // Seed Transactions
        conn.execute(
            "INSERT INTO khata_transactions (contact_id, amount, flow_type, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            params![2, 2500.0, "Credit", "Purchased 2 coils of tape and PVC pipe fittings", "2026-06-08 14:30:00"],
        )?;
        conn.execute(
            "INSERT INTO khata_transactions (contact_id, amount, flow_type, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            params![3, 12000.0, "Debit", "Pending bill for Fast Cables stock delivery", "2026-06-09 10:15:00"],
        )?;

        Ok(())
    }

    // Product methods
    pub fn get_products(&self) -> Result<Vec<Product>> {
        let conn = self.get_conn()?;
        let mut stmt = conn.prepare("SELECT id, sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id FROM products")?;
        let product_iter = stmt.query_map([], |row| {
            Ok(Product {
                id: Some(row.get(0)?),
                sku: row.get(1)?,
                name: row.get(2)?,
                category: row.get(3)?,
                stock_quantity: row.get(4)?,
                reorder_level: row.get(5)?,
                cost_price: row.get(6)?,
                selling_price: row.get(7)?,
                image_path: row.get(8)?,
                supplier_id: row.get(9)?,
            })
        })?;

        let mut products = Vec::new();
        for p in product_iter {
            products.push(p?);
        }
        Ok(products)
    }

    pub fn insert_product(&self, p: Product) -> Result<i64> {
        let conn = self.get_conn()?;
        conn.execute(
            "INSERT INTO products (sku, name, category, stock_quantity, reorder_level, cost_price, selling_price, image_path, supplier_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            params![p.sku, p.name, p.category, p.stock_quantity, p.reorder_level, p.cost_price, p.selling_price, p.image_path, p.supplier_id],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn update_product(&self, p: Product) -> Result<()> {
        let conn = self.get_conn()?;
        
        // Track price changes
        if let Some(pid) = p.id {
            if let Ok(old_price) = conn.query_row("SELECT selling_price FROM products WHERE id = ?", [pid], |row| row.get::<_, f64>(0)) {
                if (old_price - p.selling_price).abs() > 0.001 {
                    conn.execute(
                        "INSERT INTO price_history (product_id, change_date, old_price, new_price) 
                         VALUES (?, datetime('now', 'localtime'), ?, ?)",
                        params![pid, old_price, p.selling_price],
                    ).ok();
                }
            }
        }

        conn.execute(
            "UPDATE products SET sku = ?, name = ?, category = ?, stock_quantity = ?, reorder_level = ?, cost_price = ?, selling_price = ?, image_path = ?, supplier_id = ? 
             WHERE id = ?",
            params![p.sku, p.name, p.category, p.stock_quantity, p.reorder_level, p.cost_price, p.selling_price, p.image_path, p.supplier_id, p.id],
        )?;
        Ok(())
    }

    pub fn delete_product(&self, id: i64) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute("DELETE FROM products WHERE id = ?", [id])?;
        Ok(())
    }

    pub fn adjust_stock(&self, id: i64, change: f64) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?", params![change, id])?;
        Ok(())
    }

    // Contact (Grahak & Supplier) methods
    pub fn get_contacts(&self) -> Result<Vec<Contact>> {
        let conn = self.get_conn()?;
        let mut stmt = conn.prepare("SELECT id, name, phone, email, contact_type, balance FROM contacts")?;
        let contact_iter = stmt.query_map([], |row| {
            Ok(Contact {
                id: Some(row.get(0)?),
                name: row.get(1)?,
                phone: row.get(2)?,
                email: row.get(3)?,
                contact_type: row.get(4)?,
                balance: row.get(5)?,
            })
        })?;

        let mut contacts = Vec::new();
        for c in contact_iter {
            contacts.push(c?);
        }
        Ok(contacts)
    }

    pub fn insert_contact(&self, c: Contact) -> Result<i64> {
        let conn = self.get_conn()?;
        conn.execute(
            "INSERT INTO contacts (name, phone, email, contact_type, balance) VALUES (?, ?, ?, ?, ?)",
            params![c.name, c.phone, c.email, c.contact_type, c.balance],
        )?;
        Ok(conn.last_insert_rowid())
    }

    pub fn update_contact_balance(&self, id: i64, change: f64) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute("UPDATE contacts SET balance = balance + ? WHERE id = ?", params![change, id])?;
        Ok(())
    }

    // Khata Transactions methods
    pub fn get_transactions(&self, contact_id: Option<i64>) -> Result<Vec<Transaction>> {
        let conn = self.get_conn()?;
        let mut transactions = Vec::new();
        
        let row_mapper = |row: &rusqlite::Row| {
            Ok(Transaction {
                id: Some(row.get(0)?),
                contact_id: row.get(1)?,
                amount: row.get(2)?,
                flow_type: row.get(3)?,
                description: row.get(4)?,
                timestamp: row.get(5)?,
            })
        };

        if let Some(cid) = contact_id {
            let mut stmt = conn.prepare("SELECT id, contact_id, amount, flow_type, description, timestamp FROM khata_transactions WHERE contact_id = ? ORDER BY timestamp DESC")?;
            let tx_iter = stmt.query_map([cid], row_mapper)?;
            for tx in tx_iter {
                transactions.push(tx?);
            }
        } else {
            let mut stmt = conn.prepare("SELECT id, contact_id, amount, flow_type, description, timestamp FROM khata_transactions ORDER BY timestamp DESC")?;
            let tx_iter = stmt.query_map([], row_mapper)?;
            for tx in tx_iter {
                transactions.push(tx?);
            }
        }
        
        Ok(transactions)
    }

    pub fn insert_transaction(&self, tx: Transaction) -> Result<i64> {
        let conn = self.get_conn()?;
        
        // Update balance on the contact
        // Rules for Pakistani shop Easy Khata system:
        // Cash In (Grahak paying us cash, decreases Grahak's debit balance towards us) -> contact.balance increases (moves towards 0)
        // Credit/Udhaar (Grahak buying on credit, owes us money) -> contact.balance decreases (becomes more negative)
        // Cash Out (We paying suppliers, decreases our debt to them) -> contact.balance decreases (moves towards 0)
        // Debit (We buying from supplier on credit) -> contact.balance increases (becomes more positive)
        // Cash Sale (Cash checkout from POS, no net credit impact) -> 0.0
        
        let balance_change = match tx.flow_type.as_str() {
            "Cash In" => tx.amount,         // reduces their outstanding debt to us (e.g. +Rs. 1000)
            "Credit" => -tx.amount,         // they owe us more (e.g. -Rs. 1000)
            "Cash Out" => -tx.amount,        // we owe supplier less (e.g. -Rs. 5000)
            "Debit" => tx.amount,           // we owe supplier more (e.g. +Rs. 5000)
            "Cash Sale" => 0.0,             // no credit change
            _ => 0.0
        };

        conn.execute(
            "INSERT INTO khata_transactions (contact_id, amount, flow_type, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            params![tx.contact_id, tx.amount, tx.flow_type, tx.description, tx.timestamp],
        )?;

        conn.execute(
            "UPDATE contacts SET balance = balance + ? WHERE id = ?",
            params![balance_change, tx.contact_id],
        )?;

        Ok(conn.last_insert_rowid())
    }

    pub fn get_price_history(&self, product_id: i64) -> Result<Vec<PriceHistoryEntry>> {
        let conn = self.get_conn()?;
        let mut stmt = conn.prepare(
            "SELECT id, product_id, change_date, old_price, new_price 
             FROM price_history 
             WHERE product_id = ? 
             ORDER BY change_date DESC"
        )?;
        let history_iter = stmt.query_map([product_id], |row| {
            Ok(PriceHistoryEntry {
                id: Some(row.get(0)?),
                product_id: row.get(1)?,
                change_date: row.get(2)?,
                old_price: row.get(3)?,
                new_price: row.get(4)?,
            })
        })?;

        let mut list = Vec::new();
        for h in history_iter {
            list.push(h?);
        }
        Ok(list)
    }
}
