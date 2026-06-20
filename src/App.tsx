import React, { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
  Package,
  BookOpen,
  ShoppingBag,
  Cpu,
  Bot,
  Plus,
  Trash2,
  Edit2,
  Search,
  AlertTriangle,
  UserCheck,
  UserX,
  RefreshCw,
  Printer,
  X,
  Image as ImageIcon,
  Languages
} from "lucide-react";

// Types corresponding to Rust backend
interface Product {
  id?: number;
  sku: String;
  name: String;
  category: String;
  stock_quantity: number;
  reorder_level: number;
  cost_price: number;
  selling_price: number;
  image_path?: string;
  supplier_id?: number;
}

interface Contact {
  id?: number;
  name: string;
  phone: string;
  email?: string;
  contact_type: string; // "Customer" | "Supplier"
  balance: number;
}

interface Transaction {
  id?: number;
  contact_id: number;
  amount: number;
  flow_type: string; // "Cash In" | "Cash Out" | "Credit" | "Debit"
  description: string;
  timestamp: string;
}

interface ProcessInfo {
  pid: number;
  name: string;
  cpu_usage: number;
  memory: number;
}

interface SystemMetrics {
  cpu_usage: number;
  total_memory: number;
  used_memory: number;
  processes: ProcessInfo[];
}

// English and Urdu translation map
const t = {
  en: {
    title: "Mughal Tools & Hardware",
    subtitle: "Easy Khata & POS v2",
    overview: "Dukaan Overview",
    inventory: "Maal (Inventory)",
    khata: "Khata (Ledger)",
    pos: "Billing & POS",
    sales: "Bikri (Sales History)",
    diagnostics: "Server Monitor",
    stockValue: "Maal Ki Qemat (Stock Value)",
    receivables: "Udhaar Wasooli (Receivable)",
    payables: "Supplier Dena (Payable)",
    lowStock: "Low Stock Products",
    warnings: "Maal Khatam Hone Wala Hai! (Low Stock Warning)",
    reorderInfo: "Neeche diye gaye item reorder levels tak pahunch chuke hain. Baraye meharbani stock dobara mangwayein:",
    recentLedger: "Aakhri Khata Transactions (Recent Ledger)",
    viewFullLedger: "Mukammal Khata Dekhein →",
    customerSupplier: "Grahak / Supplier",
    detailsReason: "Details / Wajah",
    type: "Type",
    amountPkr: "Raqam (PKR)",
    timestamp: "Waqt (Timestamp)",
    addNewProduct: "Naya Maal Add Karein",
    searchInventory: "Maal search karein (SKU / Name)...",
    sellingPrice: "Selling Price",
    costPrice: "Cost Price",
    stockQty: "Stock Qty",
    reorderLevel: "Reorder Lvl",
    addKhataCard: "Naya Khata Add (Add Contact)",
    customerUdhaar: "Customers Udhaar (Outstanding Debt Recievables)",
    supplierDena: "Suppliers Dena (Outstanding Payables)",
    adjustKhata: "Khata Adjust",
    paymentLog: "Payment Log",
    billDetails: "Bill Details (Cart)",
    paymentMethod: "Payment Method:",
    cashSale: "Cash Sale",
    khataSale: "Khata Sale",
    selectCustomer: "Select Customer (Grahak):",
    totalAmt: "Kul Total:",
    checkoutBtn: "Sale Complete (Check Out)",
    cpuLoad: "CPU Load",
    ramUsage: "RAM Usage",
    tauriService: "Tauri Service status",
    processes: "Resource Intensive Server Processes",
    processName: "Process Name",
    aiBotTitle: "Dukaan Assistant Bot",
    aiBotBtn: "Dukaan AI Bot",
    serviceReady: "Windows Service: Configured and Ready",
    itemsCount: "Products",
    serviceStatus: "Service status:",
    checkoutSelectCust: "-- Customer Select Karein --",
    salesReport: "Sales Report",
    walkIn: "Walk-in Grahak"
  },
  ur: {
    title: "مغل ٹولز اینڈ ہارڈویئر",
    subtitle: "ایزی کھاتہ اور بلنگ سسٹم",
    overview: "دکان کا جائزہ",
    inventory: "مال (انوینٹری)",
    khata: "کھاتہ (لیجر)",
    pos: "بلنگ اور پی او ایس",
    sales: "بکری کی تفصیل (Sales History)",
    diagnostics: "سرور مانیٹر",
    stockValue: "کل مال کی قیمت (خریداری)",
    receivables: "ادھار وصولی (کسٹمرز سے)",
    payables: "سپلائر کو دینا (ادائیگی)",
    lowStock: "کم سٹاک مال",
    warnings: "مال ختم ہونے والا ہے! (وارننگ)",
    reorderInfo: "مندرجہ ذیل اشیاء ری آرڈر کی حد تک پہنچ چکی ہیں۔ براہ کرم نیا سٹاک منگوائیں:",
    recentLedger: "حالیہ کھاتہ لین دین (لیجر کی تفصیل)",
    viewFullLedger: "مکمل کھاتہ دیکھیں ←",
    customerSupplier: "گاہک / سپلائر",
    detailsReason: "تفصیل / وجہ",
    type: "قسم",
    amountPkr: "رقم (روپے)",
    timestamp: "وقت اور تاریخ",
    addNewProduct: "نیا مال شامل کریں",
    searchInventory: "مال تلاش کریں (کوڈ یا نام)...",
    sellingPrice: "فروخت کی قیمت",
    costPrice: "خریداری کی قیمت",
    stockQty: "سٹاک کی مقدار",
    reorderLevel: "الرٹ لیول",
    addKhataCard: "نیا کھاتہ کھولیں (گاہک/سپلائر)",
    customerUdhaar: "گاہکوں کا ادھار (بقایا جات)",
    supplierDena: "سپلائرز کو ادائیگی (بقایا جات)",
    adjustKhata: "کھاتہ ایڈجسٹ",
    paymentLog: "رقم لاگ کریں",
    billDetails: "بل کی تفصیلات (کارٹ)",
    paymentMethod: "ادائیگی کا طریقہ:",
    cashSale: "نقد فروخت",
    khataSale: "کھاتہ ادھار",
    selectCustomer: "گاہک منتخب کریں:",
    totalAmt: "کل ٹوٹل:",
    checkoutBtn: "بل مکمل کریں (چیک آؤٹ)",
    cpuLoad: "سی پی یو لوڈ",
    ramUsage: "ریم کا استعمال",
    tauriService: "سروس اسٹیٹس",
    processes: "سرور پروسیس لسٹ",
    processName: "پروسیس کا نام",
    aiBotTitle: "دکان اے آئی اسسٹنٹ بوٹ",
    aiBotBtn: "دکان اے آئی بوٹ",
    serviceReady: "ونڈوز سروس: تیار اور فعال",
    itemsCount: "پروڈکٹس",
    serviceStatus: "سروس کی حالت:",
    checkoutSelectCust: "-- گاہک منتخب کریں --",
    salesReport: "فروخت کی رپورٹ",
    walkIn: "بغیر کھاتہ گاہک"
  }
};

export default function App() {
  const [lang, setLang] = useState<"en" | "ur">("en");
  const [activeTab, setActiveTab] = useState<"dashboard" | "inventory" | "khata" | "pos" | "sales" | "diagnostics">("dashboard");
  
  // Data State
  const [products, setProducts] = useState<Product[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [productImages, setProductImages] = useState<{ [key: string]: string }>({});
  
  // UI & Loading States
  const [loading, setLoading] = useState(false);
  const [sysMetrics, setSysMetrics] = useState<SystemMetrics | null>(null);
  const [serviceStatus, setServiceStatus] = useState("Checking...");
  
  // Modals / Forms
  const [showProductModal, setShowProductModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [productForm, setProductForm] = useState({
    sku: "",
    name: "",
    category: "Plumbing",
    stock_quantity: 0,
    reorder_level: 5,
    cost_price: 0,
    selling_price: 0,
    supplier_id: "",
    image_base64: ""
  });

  const [showContactModal, setShowContactModal] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: "",
    phone: "",
    email: "",
    contact_type: "Customer",
    balance: 0
  });

  const [showTransactionModal, setShowTransactionModal] = useState(false);
  const [selectedContactForTx, setSelectedContactForTx] = useState<Contact | null>(null);
  const [txForm, setTxForm] = useState({
    amount: 0,
    flow_type: "Cash In",
    description: ""
  });

  // POS State
  const [posCart, setPosCart] = useState<{ product: Product; quantity: number }[]>([]);
  const [posCustomer, setPosCustomer] = useState<string>(""); // contact_id
  const [posPaymentType, setPosPaymentType] = useState<"Cash" | "Credit">("Cash");
  const [posSearch, setPosSearch] = useState("");
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [lastSaleReceipt, setLastSaleReceipt] = useState<any>(null);

  // AI State
  const [aiOpen, setAiOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiMessages, setAiMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "Assalam-o-Alaikum! Main aapka dukaan assistant hoon. Main stock ya Khata ke baare mein sawalat ke jawab de sakta hoon." }
  ]);
  const [aiLoading, setAiLoading] = useState(false);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showPriceHistoryModal, setShowPriceHistoryModal] = useState(false);
  const [priceHistory, setPriceHistory] = useState<any[]>([]);
  const [historyProductName, setHistoryProductName] = useState("");

  const loadPriceHistory = async (product: Product) => {
    try {
      const history = await invoke<any[]>("get_price_history", { id: product.id });
      setPriceHistory(history);
      setHistoryProductName(product.name as string);
      setShowPriceHistoryModal(true);
    } catch (e) {
      alert("Error loading price history: " + e);
    }
  };

  const exportInventoryCSV = () => {
    let csv = "\uFEFFSKU,Name,Category,Stock,Cost Price,Selling Price\n";
    products.forEach(p => {
      csv += `"${p.sku}","${p.name}","${p.category}",${p.stock_quantity},${p.cost_price},${p.selling_price}\n`;
    });
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `inventory_backup_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyWhatsAppReminder = (c: Contact) => {
    const message = lang === "ur" 
      ? `السلام علیکم ${c.name} صاحب، مغل ٹولز اینڈ ہارڈویئر سے آپ کا بقایا ادھار کا بیلنس Rs. ${Math.abs(c.balance).toLocaleString()} ہے۔ براہ کرم جلد از جلد ادائیگی یقینی بنائیں۔ شکریہ!`
      : `Salam ${c.name}, this is a reminder from Mughal Tools & Hardware that your outstanding balance is Rs. ${Math.abs(c.balance).toLocaleString()}. Please clear it at your earliest convenience. Thank you!`;
    
    navigator.clipboard.writeText(message).then(() => {
      alert(lang === "ur" ? "واٹس ایپ پیغام کاپی کر لیا گیا ہے!" : "WhatsApp message copied to clipboard!");
    }).catch(err => {
      console.error("Failed to copy text: ", err);
    });
  };

  const copyOrderSheet = () => {
    const lowStock = products.filter(p => p.stock_quantity <= p.reorder_level);
    if (lowStock.length === 0) return;
    
    let text = `Mughal Tools & Hardware - Low Stock Order Sheet\nGenerated on: ${new Date().toLocaleDateString()}\n\n`;
    const grouped: { [key: string]: typeof lowStock } = {};
    lowStock.forEach(p => {
      const sName = contacts.find(c => c.id === p.supplier_id)?.name || "General Supplier";
      if (!grouped[sName]) grouped[sName] = [];
      grouped[sName].push(p);
    });

    Object.keys(grouped).forEach(supplier => {
      text += `Supplier: ${supplier}\n`;
      grouped[supplier].forEach(p => {
        text += `- ${p.name} (Current Stock: ${p.stock_quantity}, Reorder Level: ${p.reorder_level})\n`;
      });
      text += `\n`;
    });

    navigator.clipboard.writeText(text).then(() => {
      alert(lang === "ur" ? "آرڈر شیٹ کاپی ہو گئی ہے!" : "Order sheet copied to clipboard!");
    });
  };

  const getDailySalesData = () => {
    const days = [];
    const salesByDay: { [key: string]: number } = {};
    
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const dateString = d.toISOString().substring(0, 10);
      days.push(dateString);
      salesByDay[dateString] = 0;
    }

    transactions
      .filter(tx => tx.flow_type === "Credit" || tx.flow_type === "Cash Sale")
      .forEach(tx => {
        const txDate = tx.timestamp.substring(0, 10);
        if (salesByDay[txDate] !== undefined) {
          salesByDay[txDate] += tx.amount;
        }
      });

    return days.map(day => {
      const d = new Date(day);
      const label = d.toLocaleDateString(lang === "ur" ? "ur-PK" : "en-US", { weekday: "short" });
      return { day, label, amount: salesByDay[day] };
    });
  };

  // Fetch all basic data
  const loadData = async () => {
    setLoading(true);
    try {
      const pList = await invoke<Product[]>("get_products");
      const cList = await invoke<Contact[]>("get_contacts");
      const tList = await invoke<Transaction[]>("get_transactions");
      
      setProducts(pList);
      setContacts(cList);
      setTransactions(tList);

      // Load base64 strings for product images
      const images: { [key: string]: string } = {};
      for (const p of pList) {
        if (p.image_path) {
          try {
            const base64 = await invoke<string>("load_product_image_base64", { path: p.image_path });
            images[p.sku as string] = base64;
          } catch (e) {
            console.error("Failed to load image for SKU", p.sku, e);
          }
        }
      }
      setProductImages(images);
    } catch (err) {
      console.error("Error loading application data", err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch system metrics
  const fetchMetrics = async () => {
    try {
      const metrics = await invoke<SystemMetrics>("get_sys_metrics");
      setSysMetrics(metrics);
      const status = await invoke<string>("check_service_status");
      setServiceStatus(status);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  // Handle Image Selection and Base64 conversion
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProductForm(prev => ({ ...prev, image_base64: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Product Save CRUD
  const saveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let imagePath = selectedProduct?.image_path || null;
      if (productForm.image_base64) {
        imagePath = await invoke<string>("save_product_image", {
          sku: productForm.sku,
          base64Data: productForm.image_base64
        });
      }

      const payload: Product = {
        id: selectedProduct?.id,
        sku: productForm.sku,
        name: productForm.name,
        category: productForm.category,
        stock_quantity: Number(productForm.stock_quantity),
        reorder_level: Number(productForm.reorder_level),
        cost_price: Number(productForm.cost_price),
        selling_price: Number(productForm.selling_price),
        image_path: imagePath || undefined,
        supplier_id: productForm.supplier_id ? Number(productForm.supplier_id) : undefined
      };

      if (selectedProduct) {
        await invoke("update_product", { product: payload });
      } else {
        await invoke("add_product", { product: payload });
      }
      setShowProductModal(false);
      setSelectedProduct(null);
      loadData();
    } catch (err) {
      alert("Error saving product: " + err);
    }
  };

  // Delete product
  const deleteProduct = async (id: number) => {
    if (confirm("Are you sure you want to delete this product?")) {
      try {
        await invoke("delete_product", { id });
        loadData();
      } catch (err) {
        alert("Error deleting product: " + err);
      }
    }
  };

  // Add Contact CRUD
  const saveContact = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: Contact = {
        name: contactForm.name,
        phone: contactForm.phone,
        email: contactForm.email || undefined,
        contact_type: contactForm.contact_type,
        balance: Number(contactForm.balance)
      };
      await invoke("add_contact", { contact: payload });
      setShowContactModal(false);
      loadData();
    } catch (err) {
      alert("Error creating contact: " + err);
    }
  };

  // Ledger transaction recording
  const saveTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedContactForTx) return;

    try {
      const now = new Date().toISOString().replace("T", " ").substring(0, 19);
      const payload: Transaction = {
        contact_id: selectedContactForTx.id!,
        amount: Number(txForm.amount),
        flow_type: txForm.flow_type,
        description: txForm.description,
        timestamp: now
      };
      await invoke("add_transaction", { transaction: payload });
      setShowTransactionModal(false);
      loadData();
    } catch (e) {
      alert("Transaction error: " + e);
    }
  };

  // POS operations
  const addToCart = (product: Product) => {
    const existing = posCart.find(item => item.product.id === product.id);
    if (existing) {
      if (existing.quantity >= product.stock_quantity) {
        alert("Aur stock available nahi hai!");
        return;
      }
      setPosCart(posCart.map(item => item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      if (product.stock_quantity < 1) {
        alert("Out of stock!");
        return;
      }
      setPosCart([...posCart, { product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId: number) => {
    setPosCart(posCart.filter(item => item.product.id !== productId));
  };

  const updateCartQuantity = (productId: number, qty: number) => {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    if (qty > product.stock_quantity) {
      alert("Stock check karein! Available stock se zyada quantity nahi de sakte.");
      return;
    }
    if (qty <= 0) {
      removeFromCart(productId);
    } else {
      setPosCart(posCart.map(item => item.product.id === productId ? { ...item, quantity: qty } : item));
    }
  };

  const calculateTotal = () => {
    return posCart.reduce((sum, item) => sum + (item.product.selling_price * item.quantity), 0);
  };

  const processSale = async () => {
    if (posCart.length === 0) return;
    if (posPaymentType === "Credit" && !posCustomer) {
      alert("Khata (Udhaar) sales ke liye Customer select karna laazmi hai!");
      return;
    }

    try {
      const now = new Date().toISOString().replace("T", " ").substring(0, 19);
      const totalAmount = calculateTotal();
      
      // Post transaction to Customer Khata (Credit) or Walk-in Grahak (Cash Sale)
      const contactId = posPaymentType === "Credit" ? Number(posCustomer) : 1;
      const customer = contacts.find(c => c.id === contactId);
      const customerName = customer ? customer.name : (posPaymentType === "Credit" ? "Customer" : "Walk-in Grahak");
      
      const tx: Transaction = {
        contact_id: contactId,
        amount: totalAmount,
        flow_type: posPaymentType === "Credit" ? "Credit" : "Cash Sale",
        description: `POS Bill (${customerName}): ${posCart.map(item => `${item.product.name} (x${item.quantity})`).join(", ")}`,
        timestamp: now
      };
      await invoke("add_transaction", { transaction: tx });

      // Deduct stock for all items
      for (const item of posCart) {
        await invoke("adjust_stock", { id: item.product.id!, change: -Number(item.quantity) });
      }

      // Generate receipt dataset
      setLastSaleReceipt({
        id: Math.floor(Math.random() * 100000),
        timestamp: now,
        items: [...posCart],
        total: totalAmount,
        paymentType: posPaymentType,
        customerName: posPaymentType === "Credit" && posCustomer ? contacts.find(c => c.id === Number(posCustomer))?.name : "Walk-in Grahak"
      });

      setPosCart([]);
      setPosCustomer("");
      setPosPaymentType("Cash");
      setShowReceiptModal(true);
      loadData();
    } catch (e) {
      alert("Error processing POS sale: " + e);
    }
  };

  // AI chat sending
  const sendAiMessage = async () => {
    if (!aiPrompt.trim()) return;
    const userMsg = { role: "user", content: aiPrompt };
    setAiMessages(prev => [...prev, userMsg]);
    setAiPrompt("");
    setAiLoading(true);
    
    try {
      const response = await invoke<string>("query_ai_chat", { prompt: userMsg.content });
      setAiMessages(prev => [...prev, { role: "assistant", content: response }]);
    } catch (e) {
      setAiMessages(prev => [...prev, { role: "assistant", content: "Sorry Bhai, AI dynamic request fetch nahi kar saka: " + e }]);
    } finally {
      setAiLoading(false);
    }
  };

  // Compute shop summaries for Pakistani Shop
  const totalStockValue = products.reduce((sum, p) => sum + (p.stock_quantity * p.cost_price), 0);
  const totalReceivables = contacts.filter(c => c.contact_type === "Customer" && c.balance < 0).reduce((sum, c) => sum + Math.abs(c.balance), 0);
  const totalPayables = contacts.filter(c => c.contact_type === "Supplier" && c.balance > 0).reduce((sum, c) => sum + c.balance, 0);
  const lowStockCount = products.filter(p => p.stock_quantity <= p.reorder_level).length;

  // Translation helpers
  const activeStrings = t[lang];

  return (
    <div className={`flex h-screen bg-slate-950 text-slate-100 overflow-hidden ${
      lang === "ur" ? "font-urdu rtl text-[16px] leading-loose" : "font-sans ltr text-sm"
    }`}>
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-6">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-emerald-500/10 p-2.5 rounded-lg border border-emerald-500/20 text-emerald-400">
              <ShoppingBag className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight text-white">{activeStrings.title}</h1>
              <span className="text-xs text-slate-400 font-mono">{activeStrings.subtitle}</span>
            </div>
          </div>

          <nav className="space-y-2">
            {[
              { id: "dashboard", label: activeStrings.overview, icon: BookOpen },
              { id: "inventory", label: activeStrings.inventory, icon: Package },
              { id: "khata", label: activeStrings.khata, icon: BookOpen },
              { id: "pos", label: activeStrings.pos, icon: ShoppingBag },
              { id: "sales", label: activeStrings.sales, icon: Printer },
              { id: "diagnostics", label: activeStrings.diagnostics, icon: Cpu }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                    activeTab === tab.id
                      ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/10"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => setAiOpen(true)}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-medium py-3 px-4 rounded-xl shadow-lg hover:brightness-110 transition-all duration-200"
          >
            <Bot className="w-5 h-5" />
            {activeStrings.aiBotBtn}
          </button>
          <div className="text-[10px] text-slate-500 text-center font-mono border-t border-slate-800 pt-4">
            {activeStrings.serviceStatus} <span className="text-emerald-400">{serviceStatus}</span>
          </div>
        </div>
      </aside>

      {/* Main Viewport */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-y-auto">
        <header className="h-16 border-b border-slate-900 px-8 flex items-center justify-between bg-slate-950/80 backdrop-blur sticky top-0 z-30">
          <h2 className="text-xl font-semibold text-white capitalize">
            {activeTab === "dashboard" ? activeStrings.overview : activeStrings[activeTab]}
          </h2>
          <div className="flex items-center gap-4">
            {/* Language Toggle */}
            <button
              onClick={() => setLang(lang === "en" ? "ur" : "en")}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-emerald-400 hover:text-white transition"
            >
              <Languages className="w-4 h-4" />
              <span>{lang === "en" ? "اردو" : "English"}</span>
            </button>
            <button
              onClick={loadData}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-all duration-200"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin text-emerald-400" : ""}`} />
            </button>
            <div className="text-sm font-mono bg-slate-900 border border-slate-800 py-1.5 px-3 rounded-lg text-emerald-400">
              Rs. {products.length} {activeStrings.itemsCount}
            </div>
          </div>
        </header>

        <div className="flex-1 p-8">
          {/* TAB 1: DASHBOARD */}
          {activeTab === "dashboard" && (
            <div className="space-y-8">
              {/* Pakistani Shop Quick Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-sm">
                  <span className="text-xs text-slate-400 font-medium">{activeStrings.stockValue}</span>
                  <div className="text-2xl font-bold text-white mt-1">Rs. {totalStockValue.toLocaleString()}</div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-sm">
                  <span className="text-xs text-slate-400 font-medium">{activeStrings.receivables}</span>
                  <div className="text-2xl font-bold text-amber-400 mt-1">Rs. {totalReceivables.toLocaleString()}</div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-sm">
                  <span className="text-xs text-slate-400 font-medium">{activeStrings.payables}</span>
                  <div className="text-2xl font-bold text-rose-400 mt-1">Rs. {totalPayables.toLocaleString()}</div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-sm">
                  <span className="text-xs text-slate-400 font-medium">{activeStrings.lowStock}</span>
                  <div className="text-2xl font-bold text-red-400 mt-1">{lowStockCount}</div>
                </div>
              </div>

              {/* Low Stock Alerts */}
              {lowStockCount > 0 && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 flex items-start gap-4">
                  <div className="bg-red-500/20 p-3 rounded-xl text-red-400">
                    <AlertTriangle className="w-6 h-6 animate-bounce" />
                  </div>
                  <div>
                    <h3 className="text-red-400 font-bold">{activeStrings.warnings}</h3>
                    <p className="text-slate-300 text-sm mt-1">{activeStrings.reorderInfo}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {products
                        .filter(p => p.stock_quantity <= p.reorder_level)
                        .map(p => (
                          <span key={p.sku as string} className="bg-slate-950 border border-red-500/30 px-3 py-1 rounded-full text-xs font-mono text-slate-300">
                            {p.name} ({p.stock_quantity})
                          </span>
                        ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Daily Sales Chart Widget */}
              {(() => {
                const dailySales = getDailySalesData();
                const maxVal = Math.max(...dailySales.map(d => d.amount), 1000);
                return (
                  <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6 shadow-sm">
                    <h3 className="font-bold text-lg text-white mb-6">
                      {lang === "ur" ? "روزانہ فروخت کی کارکردگی (گزشتہ 7 دن)" : "Daily Sales Performance (Last 7 Days)"}
                    </h3>
                    <div className="flex items-end justify-between gap-4 h-64 px-4 pt-4 bg-slate-950/40 rounded-xl border border-slate-850">
                      {dailySales.map((dayData, idx) => {
                        const heightPercent = (dayData.amount / maxVal) * 80;
                        return (
                          <div key={idx} className="flex-1 flex flex-col items-center group cursor-pointer">
                            <span className="text-[10px] text-emerald-450 font-mono opacity-0 group-hover:opacity-100 transition-opacity duration-200 mb-1">
                              Rs. {dayData.amount.toLocaleString()}
                            </span>
                            <div className="w-full bg-slate-900/50 rounded-t-lg relative overflow-hidden flex items-end h-40 border border-slate-800">
                              <div 
                                className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t-lg transition-all duration-500 ease-out group-hover:brightness-110 shadow-lg shadow-emerald-500/10"
                                style={{ height: `${Math.max(4, heightPercent)}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-400 mt-2 font-medium">{dayData.label}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })()}

              {/* Recent Transactions Ledger */}
              <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-bold text-lg text-white">{activeStrings.recentLedger}</h3>
                  <button
                    onClick={() => setActiveTab("khata")}
                    className="text-emerald-400 hover:text-emerald-300 text-xs font-medium"
                  >
                    {activeStrings.viewFullLedger}
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="py-3">{activeStrings.customerSupplier}</th>
                        <th className="py-3">{activeStrings.detailsReason}</th>
                        <th className="py-3">{activeStrings.type}</th>
                        <th className="py-3 text-right">{activeStrings.amountPkr}</th>
                        <th className="py-3 text-right">{activeStrings.timestamp}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.slice(0, 5).map(tx => {
                        const contact = contacts.find(c => c.id === tx.contact_id);
                        const isOutflow = tx.flow_type === "Cash Out" || tx.flow_type === "Credit";
                        return (
                          <tr key={tx.id} className="border-b border-slate-800/50 hover:bg-slate-900/20">
                            <td className="py-3 font-semibold text-white">{contact?.name || "Unknown"}</td>
                            <td className="py-3 text-slate-400">{tx.description}</td>
                            <td className="py-3">
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                                tx.flow_type === "Cash In" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                                tx.flow_type === "Credit" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                                tx.flow_type === "Debit" ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" :
                                "bg-slate-800 text-slate-400"
                              }`}>
                                {tx.flow_type}
                              </span>
                            </td>
                            <td className={`py-3 text-right font-mono font-bold ${isOutflow ? "text-rose-400" : "text-emerald-400"}`}>
                              Rs. {tx.amount.toLocaleString()}
                            </td>
                            <td className="py-3 text-right text-xs text-slate-500">{tx.timestamp}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: INVENTORY */}
          {activeTab === "inventory" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div className="relative w-80">
                  <Search className="w-5 h-5 absolute left-3 top-2.5 text-slate-500" />
                  <input
                    type="text"
                    placeholder={activeStrings.searchInventory}
                    onChange={(e) => setPosSearch(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-850 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={exportInventoryCSV}
                    className="bg-slate-900 border border-slate-800 text-slate-350 px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 hover:bg-slate-805 transition"
                  >
                    {lang === "ur" ? "CSV ایکسپورٹ" : "Export CSV"}
                  </button>
                  <button
                    onClick={() => setShowOrderModal(true)}
                    className="bg-slate-900 border border-slate-800 text-slate-350 px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 hover:bg-slate-805 transition"
                  >
                    {lang === "ur" ? "آرڈر شیٹ بنائیں" : "Create Order Sheet"}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedProduct(null);
                      setProductForm({
                        sku: `SKU-${Math.floor(1000 + Math.random() * 9000)}`,
                        name: "",
                        category: "Plumbing",
                        stock_quantity: 0,
                        reorder_level: 5,
                        cost_price: 0,
                        selling_price: 0,
                        supplier_id: "",
                        image_base64: ""
                      });
                      setShowProductModal(true);
                    }}
                    className="bg-emerald-500 text-white px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 hover:bg-emerald-400 transition"
                  >
                    <Plus className="w-5 h-5" /> {activeStrings.addNewProduct}
                  </button>
                </div>
              </div>

              {/* Product Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {products
                  .filter(p => p.name.toLowerCase().includes(posSearch.toLowerCase()) || p.sku.toLowerCase().includes(posSearch.toLowerCase()))
                  .map(p => {
                    const isLowStock = p.stock_quantity <= p.reorder_level;
                    const imageSrc = productImages[p.sku as string] || "/tauri.svg";
                    return (
                      <div key={p.id} className={`bg-slate-900/40 border rounded-2xl p-5 shadow flex flex-col justify-between ${
                        isLowStock ? "border-red-500/30 bg-red-500/[0.01]" : "border-slate-800"
                      }`}>
                        <div>
                          <div className="w-full h-36 bg-slate-950 rounded-xl mb-4 overflow-hidden border border-slate-800 flex items-center justify-center relative">
                            {productImages[p.sku as string] ? (
                              <img src={imageSrc} className="w-full h-full object-cover" alt="Product" />
                            ) : (
                              <div className="text-slate-600 flex flex-col items-center gap-2">
                                <ImageIcon className="w-8 h-8" />
                                <span className="text-[10px] font-mono">No Image</span>
                              </div>
                            )}
                            {isLowStock && (
                              <span className="absolute top-2 right-2 bg-red-500 text-white font-bold text-[9px] px-2 py-0.5 rounded-full tracking-wide">
                                LOW STOCK
                              </span>
                            )}
                          </div>

                          <span className="text-[10px] text-emerald-400 font-mono tracking-wider font-bold">{p.category}</span>
                          <h4 className="font-bold text-white text-md mt-1 truncate">{p.name}</h4>
                          <span className="text-xs text-slate-500 font-mono block mt-0.5">{p.sku}</span>
                          
                          <div className="grid grid-cols-2 gap-2 mt-4 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                            <div>
                              <span className="text-[10px] text-slate-500 block">{activeStrings.stockQty}</span>
                              <span className="font-bold text-sm font-mono">{p.stock_quantity}</span>
                            </div>
                            <div>
                              <span className="text-[10px] text-slate-500 block">{activeStrings.reorderLevel}</span>
                              <span className="font-bold text-sm font-mono text-slate-400">{p.reorder_level}</span>
                            </div>
                          </div>
                        </div>

                        <div className="mt-5 border-t border-slate-800/50 pt-4 flex items-center justify-between">
                          <div>
                            <span className="text-[10px] text-slate-500 block">{activeStrings.sellingPrice}</span>
                            <span className="font-bold text-emerald-400 font-mono text-md">Rs. {p.selling_price.toLocaleString()}</span>
                          </div>

                          <div className="flex gap-2">
                            <button
                              onClick={() => loadPriceHistory(p)}
                              className="px-2 py-1 bg-slate-950 border border-slate-800 text-slate-450 hover:text-emerald-450 rounded-lg transition text-[11px] font-bold"
                              title={lang === "ur" ? "قیمت کی ہسٹری" : "Price History"}
                            >
                              Rs. Hist
                            </button>
                            <button
                              onClick={() => {
                                setSelectedProduct(p);
                                setProductForm({
                                  sku: p.sku as string,
                                  name: p.name as string,
                                  category: p.category as string,
                                  stock_quantity: p.stock_quantity,
                                  reorder_level: p.reorder_level,
                                  cost_price: p.cost_price,
                                  selling_price: p.selling_price,
                                  supplier_id: p.supplier_id ? p.supplier_id.toString() : "",
                                  image_base64: ""
                                });
                                setShowProductModal(true);
                              }}
                              className="p-2 bg-slate-950 border border-slate-800 text-slate-400 hover:text-white rounded-lg transition"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteProduct(p.id!)}
                              className="p-2 bg-slate-950 border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white rounded-lg transition"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* TAB 3: KHATA */}
          {activeTab === "khata" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-lg text-white">{activeStrings.khata}</h3>
                <button
                  onClick={() => {
                    setContactForm({
                      name: "",
                      phone: "",
                      email: "",
                      contact_type: "Customer",
                      balance: 0
                    });
                    setShowContactModal(true);
                  }}
                  className="bg-emerald-500 text-white px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 hover:bg-emerald-400 transition"
                >
                  <Plus className="w-5 h-5" /> {activeStrings.addKhataCard}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Customers Ledger */}
                <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6">
                  <h4 className="font-bold text-md text-amber-400 mb-4 flex items-center gap-2">
                    <UserX className="w-5 h-5" /> {activeStrings.customerUdhaar}
                  </h4>
                  <div className="space-y-4">
                    {contacts
                      .filter(c => c.contact_type === "Customer")
                      .map(c => (
                        <div key={c.id} className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl flex items-center justify-between">
                          <div>
                            <span className="font-bold text-white block">{c.name}</span>
                            <span className="text-xs text-slate-500 font-mono">{c.phone}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <span className="text-[10px] text-slate-500 block">
                                {c.balance < 0 
                                  ? (lang === "en" ? "Outstanding" : "بقایا ادھار")
                                  : (lang === "en" ? "Advance" : "پیشگی رقم")}
                              </span>
                              <span className={`font-bold font-mono text-sm ${c.balance < 0 ? "text-amber-400" : "text-emerald-450"}`}>
                                Rs. {Math.abs(c.balance).toLocaleString()}
                              </span>
                            </div>
                            <div className="flex gap-2">
                              {c.balance < 0 && (
                                <button
                                  onClick={() => copyWhatsAppReminder(c)}
                                  className="bg-emerald-950/20 hover:bg-emerald-500 hover:text-white border border-emerald-500/20 text-emerald-400 font-semibold px-2.5 py-1.5 rounded-lg text-xs transition"
                                >
                                  {lang === "en" ? "Copy Wasooli" : "وصولی پیغام کاپی"}
                                </button>
                              )}
                              <button
                                onClick={() => {
                                  setSelectedContactForTx(c);
                                  setTxForm({ amount: 0, flow_type: "Cash In", description: "" });
                                  setShowTransactionModal(true);
                                }}
                                className="bg-slate-900 hover:bg-slate-850 border border-slate-800 text-slate-350 font-semibold px-3 py-1.5 rounded-lg text-xs"
                              >
                                {activeStrings.adjustKhata}
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Suppliers Ledger */}
                <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6">
                  <h4 className="font-bold text-md text-emerald-400 mb-4 flex items-center gap-2">
                    <UserCheck className="w-5 h-5" /> {activeStrings.supplierDena}
                  </h4>
                  <div className="space-y-4">
                    {contacts
                      .filter(c => c.contact_type === "Supplier")
                      .map(c => (
                        <div key={c.id} className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl flex items-center justify-between">
                          <div>
                            <span className="font-bold text-white block">{c.name}</span>
                            <span className="text-xs text-slate-500 font-mono">{c.phone}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <span className="text-[10px] text-slate-500 block">
                                {c.balance >= 0 
                                  ? (lang === "en" ? "We owe them" : "ہم نے دینا ہے")
                                  : (lang === "en" ? "Paid Advance" : "پیشگی ادائیگی")}
                              </span>
                              <span className={`font-bold font-mono text-sm ${c.balance >= 0 ? "text-rose-450" : "text-emerald-450"}`}>
                                Rs. {Math.abs(c.balance).toLocaleString()}
                              </span>
                            </div>
                            <button
                              onClick={() => {
                                setSelectedContactForTx(c);
                                setTxForm({ amount: 0, flow_type: "Cash Out", description: "" });
                                setShowTransactionModal(true);
                              }}
                              className="bg-slate-900 hover:bg-slate-850 border border-slate-800 text-slate-300 font-semibold px-3 py-1.5 rounded-lg text-xs"
                            >
                              {activeStrings.paymentLog}
                            </button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: POS & BILLING */}
          {activeTab === "pos" && (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 h-[calc(100vh-12rem)]">
              {/* Product Selection Column */}
              <div className="md:col-span-8 flex flex-col h-full bg-slate-900/20 border border-slate-900 rounded-2xl p-6">
                <div className="mb-4 relative">
                  <Search className="w-5 h-5 absolute left-3 top-2.5 text-slate-500" />
                  <input
                    type="text"
                    placeholder={activeStrings.searchInventory}
                    onChange={(e) => setPosSearch(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-emerald-500 text-white"
                  />
                </div>

                <div className="flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-3 gap-4 pr-2">
                  {products
                    .filter(p => p.name.toLowerCase().includes(posSearch.toLowerCase()) || p.sku.toLowerCase().includes(posSearch.toLowerCase()))
                    .map(p => (
                      <button
                        key={p.id}
                        onClick={() => addToCart(p)}
                        disabled={p.stock_quantity === 0}
                        className={`p-4 rounded-xl border flex flex-col text-left transition ${
                          p.stock_quantity === 0
                            ? "bg-slate-950/20 border-slate-900 cursor-not-allowed opacity-50"
                            : "bg-slate-900/40 border-slate-800 hover:border-emerald-500/50 hover:bg-slate-900/60"
                        }`}
                      >
                        <span className="text-slate-400 font-mono text-[9px] block uppercase">{p.sku}</span>
                        <span className="font-bold text-white text-sm mt-1 truncate w-full">{p.name}</span>
                        
                        <div className="flex justify-between items-center w-full mt-4">
                          <span className="text-emerald-400 font-bold font-mono text-xs">Rs. {p.selling_price}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                            p.stock_quantity <= p.reorder_level ? "bg-red-500/10 text-red-400" : "bg-slate-950 text-slate-400"
                          }`}>
                            Qty: {p.stock_quantity}
                          </span>
                        </div>
                      </button>
                    ))}
                </div>
              </div>

              {/* Cart / Checkout Column */}
              <div className="md:col-span-4 flex flex-col h-full bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <h3 className="font-bold text-lg text-white border-b border-slate-800 pb-3">{activeStrings.billDetails}</h3>
                
                {/* Cart Items List */}
                <div className="flex-1 overflow-y-auto py-4 space-y-3">
                  {posCart.map(item => (
                    <div key={item.product.id} className="bg-slate-950 p-3 rounded-xl border border-slate-850 flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <span className="font-bold text-white text-xs block truncate">{item.product.name}</span>
                        <span className="text-[10px] text-slate-500 font-mono block">Rs. {item.product.selling_price} / unit</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => updateCartQuantity(item.product.id!, Number(e.target.value))}
                          className="w-12 bg-slate-900 border border-slate-800 text-center text-xs py-1 rounded font-mono text-white"
                        />
                        <button
                          onClick={() => removeFromCart(item.product.id!)}
                          className="p-1.5 text-rose-500 hover:bg-rose-500/10 rounded-lg transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {posCart.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
                      Cart empty hai. Items select karein!
                    </div>
                  )}
                </div>

                {/* POS Settings & Checkout */}
                <div className="border-t border-slate-800 pt-4 space-y-4">
                  <div className="flex items-center justify-between text-sm text-slate-400">
                    <span>{activeStrings.paymentMethod}</span>
                    <div className="flex gap-2 bg-slate-950 p-1 rounded-lg border border-slate-850">
                      <button
                        onClick={() => setPosPaymentType("Cash")}
                        className={`px-3 py-1 rounded text-xs font-semibold ${
                          posPaymentType === "Cash" ? "bg-emerald-500 text-white" : "text-slate-400 hover:text-white"
                        }`}
                      >
                        {activeStrings.cashSale}
                      </button>
                      <button
                        onClick={() => setPosPaymentType("Credit")}
                        className={`px-3 py-1 rounded text-xs font-semibold ${
                          posPaymentType === "Credit" ? "bg-amber-500 text-white" : "text-slate-400 hover:text-white"
                        }`}
                      >
                        {activeStrings.khataSale}
                      </button>
                    </div>
                  </div>

                  {posPaymentType === "Credit" && (
                    <div className="space-y-1">
                      <label className="text-xs text-slate-400">{activeStrings.selectCustomer}</label>
                      <select
                        value={posCustomer}
                        onChange={(e) => setPosCustomer(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                      >
                        <option value="">{activeStrings.checkoutSelectCust}</option>
                        {contacts
                          .filter(c => c.contact_type === "Customer")
                          .map(c => (
                            <option key={c.id} value={c.id}>{c.name} ({c.phone})</option>
                          ))}
                      </select>
                    </div>
                  )}

                  <div className="flex justify-between items-center text-lg font-bold text-white border-t border-slate-850 pt-3">
                    <span>{activeStrings.totalAmt}</span>
                    <span className="font-mono text-emerald-400 text-xl">Rs. {calculateTotal().toLocaleString()}</span>
                  </div>

                  <button
                    onClick={processSale}
                    disabled={posCart.length === 0}
                    className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-white font-bold py-3 rounded-xl shadow-lg transition"
                  >
                    {activeStrings.checkoutBtn}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: DIAGNOSTICS */}
          {activeTab === "diagnostics" && (
            <div className="space-y-6">
              {/* Server Usage KPIs */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                  <span className="text-xs text-slate-400 font-semibold block">{activeStrings.cpuLoad}</span>
                  <div className="text-3xl font-mono font-bold text-emerald-400 mt-2">
                    {sysMetrics ? sysMetrics.cpu_usage.toFixed(1) : "0.0"} %
                  </div>
                  <div className="w-full bg-slate-950 h-2 rounded-full mt-4 overflow-hidden border border-slate-800">
                    <div
                      className="bg-emerald-400 h-full transition-all duration-300"
                      style={{ width: `${sysMetrics ? Math.min(100, sysMetrics.cpu_usage) : 0}%` }}
                    />
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                  <span className="text-xs text-slate-400 font-semibold block">{activeStrings.ramUsage}</span>
                  <div className="text-3xl font-mono font-bold text-emerald-400 mt-2">
                    {sysMetrics ? (sysMetrics.used_memory / 1024 / 1024 / 1024).toFixed(2) : "0.0"} GB
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    Total: {sysMetrics ? (sysMetrics.total_memory / 1024 / 1024 / 1024).toFixed(2) : "0.0"} GB
                  </div>
                  <div className="w-full bg-slate-950 h-2 rounded-full mt-4 overflow-hidden border border-slate-800">
                    <div
                      className="bg-emerald-400 h-full transition-all duration-300"
                      style={{
                        width: `${sysMetrics ? (sysMetrics.used_memory / sysMetrics.total_memory) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                  <span className="text-xs text-slate-400 font-semibold block">{activeStrings.tauriService}</span>
                  <div className="text-md font-semibold text-white mt-2">
                    Windows daemon backend
                  </div>
                  <div className="text-[10px] text-emerald-400 font-mono mt-1">
                    {serviceStatus}
                  </div>
                </div>
              </div>

              {/* Running Processes Table */}
              <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6">
                <h3 className="font-bold text-md text-white mb-4">{activeStrings.processes}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-350">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                        <th className="py-2.5">{activeStrings.processName}</th>
                        <th className="py-2.5">PID</th>
                        <th className="py-2.5 text-right">CPU (%)</th>
                        <th className="py-2.5 text-right">Memory (MB)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sysMetrics?.processes.map((proc, index) => (
                        <tr key={index} className="border-b border-slate-850 hover:bg-slate-900/25">
                          <td className="py-2 font-semibold text-slate-200">{proc.name}</td>
                          <td className="py-2 font-mono text-slate-500">{proc.pid}</td>
                          <td className="py-2 text-right font-mono text-emerald-400 font-bold">{proc.cpu_usage.toFixed(1)} %</td>
                          <td className="py-2 text-right font-mono text-slate-400">{(proc.memory / 1024 / 1024).toFixed(1)} MB</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: SALES HISTORY */}
          {activeTab === "sales" && (
            <div className="space-y-6">
              {/* Sales Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-lg shadow-emerald-950/5">
                  <span className="text-xs text-slate-400 font-semibold block">{lang === "en" ? "Total Sales Value" : "کل فروخت کی مالیت"}</span>
                  <div className="text-3xl font-mono font-bold text-emerald-400 mt-2">
                    Rs. {transactions
                      .filter(tx => tx.flow_type === "Credit" || tx.flow_type === "Cash Sale")
                      .reduce((sum, tx) => sum + tx.amount, 0)
                      .toLocaleString()}
                  </div>
                </div>

                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-lg shadow-amber-950/5">
                  <span className="text-xs text-slate-400 font-semibold block">{lang === "en" ? "Cash Sales" : "نقد فروخت کا مجموعہ"}</span>
                  <div className="text-3xl font-mono font-bold text-amber-400 mt-2">
                    Rs. {transactions
                      .filter(tx => tx.flow_type === "Cash Sale")
                      .reduce((sum, tx) => sum + tx.amount, 0)
                      .toLocaleString()}
                  </div>
                </div>

                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-lg shadow-rose-950/5">
                  <span className="text-xs text-slate-400 font-semibold block">{lang === "en" ? "Credit Sales (Udhaar)" : "ادھار فروخت کا مجموعہ"}</span>
                  <div className="text-3xl font-mono font-bold text-rose-400 mt-2">
                    Rs. {transactions
                      .filter(tx => tx.flow_type === "Credit")
                      .reduce((sum, tx) => sum + tx.amount, 0)
                      .toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Sales Invoice List */}
              <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6">
                <h3 className="font-bold text-md text-white mb-4">{lang === "en" ? "All Sales Invoices" : "تمام فروخت کے بل"}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-350">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                        <th className="py-2.5">{lang === "en" ? "Customer" : "گاہک"}</th>
                        <th className="py-2.5">{lang === "en" ? "Items Summary" : "پروڈکٹس کی تفصیل"}</th>
                        <th className="py-2.5">{lang === "en" ? "Type" : "قسم"}</th>
                        <th className="py-2.5 text-right">{lang === "en" ? "Amount (Rs.)" : "رقم (روپے)"}</th>
                        <th className="py-2.5 text-right">{lang === "en" ? "Date & Time" : "تاریخ اور وقت"}</th>
                        <th className="py-2.5 text-center">{lang === "en" ? "Action" : "کام"}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions
                        .filter(tx => tx.flow_type === "Credit" || tx.flow_type === "Cash Sale")
                        .map((tx, index) => {
                          const contact = contacts.find(c => c.id === tx.contact_id);
                          return (
                            <tr key={index} className="border-b border-slate-850 hover:bg-slate-900/25">
                              <td className="py-3 font-semibold text-slate-200">{contact?.name || "Walk-in Grahak"}</td>
                              <td className="py-3 text-slate-400 max-w-xs truncate">{tx.description.replace(/^POS Bill \([^)]+\):\s*/, "")}</td>
                              <td className="py-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  tx.flow_type === "Cash Sale" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/25" : "bg-rose-500/10 text-rose-400 border border-rose-500/25"
                                }`}>
                                  {tx.flow_type === "Cash Sale" ? "Cash" : "Credit"}
                                </span>
                              </td>
                              <td className="py-3 text-right font-mono text-slate-200 font-bold">Rs. {tx.amount.toLocaleString()}</td>
                              <td className="py-3 text-right font-mono text-slate-500">{tx.timestamp}</td>
                              <td className="py-3 text-center">
                                <button
                                  onClick={() => {
                                    // Reconstruct receipt format
                                    setLastSaleReceipt({
                                      id: tx.id || Math.floor(Math.random() * 100000),
                                      timestamp: tx.timestamp,
                                      items: [],
                                      total: tx.amount,
                                      paymentType: tx.flow_type === "Cash Sale" ? "Cash" : "Credit",
                                      customerName: contact?.name || "Walk-in Grahak",
                                      isHistorical: true,
                                      description: tx.description
                                    });
                                    setShowReceiptModal(true);
                                  }}
                                  className="text-emerald-400 hover:text-emerald-300 font-semibold px-2 py-1 bg-slate-950 border border-slate-850 rounded hover:border-emerald-500 transition"
                                >
                                  {lang === "en" ? "View Raseed" : "رسید دیکھیں"}
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* AI Bot Chat Drawer */}
      {aiOpen && (
        <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-850 shadow-2xl flex flex-col z-50">
          <div className="h-16 border-b border-slate-850 px-6 flex items-center justify-between">
            <div className="flex items-center gap-2 text-white font-bold">
              <Bot className="w-5 h-5 text-emerald-400" />
              <span>{activeStrings.aiBotTitle}</span>
            </div>
            <button
              onClick={() => setAiOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {aiMessages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`p-3.5 rounded-2xl max-w-[85%] text-xs line-clamp-none ${
                    msg.role === "user"
                      ? "bg-emerald-500 text-white rounded-tr-none"
                      : "bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-none"
                  }`}
                >
                  <p className="whitespace-pre-line font-medium leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))}
            {aiLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-2xl rounded-tl-none flex items-center gap-2 text-xs text-slate-400">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Box */}
          <div className="p-4 border-t border-slate-850 bg-slate-950/80">
            <div className="flex gap-2">
              <input
                type="text"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendAiMessage()}
                placeholder="Ask about inventory or customer Khata..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
              <button
                onClick={sendAiMessage}
                className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold p-2.5 rounded-xl transition"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 1: ADD / EDIT PRODUCT */}
      {showProductModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="font-bold text-lg text-white">
                {selectedProduct ? "Maal Edit Karein" : "Naya Maal Add Karein"}
              </h3>
              <button onClick={() => setShowProductModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={saveProduct} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">SKU Barcode</label>
                  <input
                    type="text"
                    required
                    value={productForm.sku}
                    onChange={(e) => setProductForm({ ...productForm, sku: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Category</label>
                  <select
                    value={productForm.category}
                    onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  >
                    <option value="Plumbing">Plumbing</option>
                    <option value="Electrical">Electrical</option>
                    <option value="Fasteners">Fasteners</option>
                    <option value="Paint">Paint</option>
                    <option value="Tools">Tools</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-400">Product Name (Item Name)</label>
                <input
                  type="text"
                  required
                  value={productForm.name}
                  onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                  placeholder="e.g. Berger Paint 1L Matte"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Stock Quantity</label>
                  <input
                    type="number"
                    required
                    value={productForm.stock_quantity}
                    onChange={(e) => setProductForm({ ...productForm, stock_quantity: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Reorder Alert Level</label>
                  <input
                    type="number"
                    required
                    value={productForm.reorder_level}
                    onChange={(e) => setProductForm({ ...productForm, reorder_level: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Cost Price (Khareed Qemat)</label>
                  <input
                    type="number"
                    required
                    value={productForm.cost_price}
                    onChange={(e) => setProductForm({ ...productForm, cost_price: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Selling Price (Farokht Qemat)</label>
                  <input
                    type="number"
                    required
                    value={productForm.selling_price}
                    onChange={(e) => setProductForm({ ...productForm, selling_price: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-400">Product Image Upload</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-400"
                />
              </div>

              <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowProductModal(false)}
                  className="px-4 py-2 border border-slate-800 text-slate-400 text-xs font-semibold rounded-lg hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: ADD CONTACT (KHATA REGISTER) */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="font-bold text-lg text-white">Naya Khata Add Karein</h3>
              <button onClick={() => setShowContactModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={saveContact} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-400">Full Name (Pura Naam)</label>
                <input
                  type="text"
                  required
                  value={contactForm.name}
                  onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                  placeholder="e.g. Kamran Bhai"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-400">Phone Number (Mobile)</label>
                <input
                  type="text"
                  required
                  value={contactForm.phone}
                  onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                  placeholder="e.g. 0300-1234567"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-400">Email Address (Optional)</label>
                <input
                  type="email"
                  value={contactForm.email}
                  onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Contact Type</label>
                  <select
                    value={contactForm.contact_type}
                    onChange={(e) => setContactForm({ ...contactForm, contact_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  >
                    <option value="Customer">Customer (Grahak)</option>
                    <option value="Supplier">Supplier (Hokdaar)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Opening Balance (PKR)</label>
                  <input
                    type="number"
                    value={contactForm.balance}
                    onChange={(e) => setContactForm({ ...contactForm, balance: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowContactModal(false)}
                  className="px-4 py-2 border border-slate-800 text-slate-400 text-xs font-semibold rounded-lg hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg"
                >
                  Save Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: ADJUST TRANSACTION */}
      {showTransactionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="font-bold text-lg text-white">
                Khata Transaction: {selectedContactForTx?.name}
              </h3>
              <button onClick={() => setShowTransactionModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={saveTransaction} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Transaction Type</label>
                  <select
                    value={txForm.flow_type}
                    onChange={(e) => setTxForm({ ...txForm, flow_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  >
                    {selectedContactForTx?.contact_type === "Customer" ? (
                      <>
                        <option value="Cash In">Cash In (Payment received)</option>
                        <option value="Credit">Credit (Udhaar check/sales)</option>
                      </>
                    ) : (
                      <>
                        <option value="Cash Out">Cash Out (Paid to Supplier)</option>
                        <option value="Debit">Debit (Purchased on credit)</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Raqam / Amount (Rs.)</label>
                  <input
                    type="number"
                    required
                    value={txForm.amount}
                    onChange={(e) => setTxForm({ ...txForm, amount: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-400">Description (Wajah / Details)</label>
                <input
                  type="text"
                  required
                  value={txForm.description}
                  onChange={(e) => setTxForm({ ...txForm, description: e.target.value })}
                  placeholder="e.g. Paid full cash or Took PVC pipeline pipe fittings"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowTransactionModal(false)}
                  className="px-4 py-2 border border-slate-800 text-slate-400 text-xs font-semibold rounded-lg hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg"
                >
                  Post Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 4: RASEED (POS PRINT INVOICE MOCK) */}
      {showReceiptModal && lastSaleReceipt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-white text-slate-900 rounded-2xl w-full max-w-sm p-6 space-y-6 print:p-0 print:border-none print:shadow-none shadow-2xl relative">
            <button
              onClick={() => {
                setShowReceiptModal(false);
                setLastSaleReceipt(null);
              }}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-800 print:hidden"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Receipt layout */}
            <div className="text-center font-mono">
              <h3 className="font-bold text-lg uppercase tracking-tight">{activeStrings.title}</h3>
              <p className="text-xs text-slate-500">Mianwali Road, Near Millat Chowk, Pakistan</p>
              <p className="text-xs text-slate-500">Tel: 0300-1234567</p>
              
              <div className="border-y border-dashed border-slate-300 my-4 py-2 text-left text-xs space-y-1">
                <div>Receipt #: {lastSaleReceipt.id}</div>
                <div>Date: {lastSaleReceipt.timestamp}</div>
                <div>Grahak: {lastSaleReceipt.customerName}</div>
                <div>Payment Mode: {lastSaleReceipt.paymentType}</div>
              </div>

              <div className="text-left text-xs space-y-2 font-sans">
                {lastSaleReceipt.isHistorical ? (
                  <div className="bg-slate-50 p-3 rounded border border-slate-200 text-slate-700 whitespace-pre-wrap text-[11px] leading-relaxed">
                    {lastSaleReceipt.description}
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-12 font-bold border-b pb-1 font-mono">
                      <div className="col-span-6">Item</div>
                      <div className="col-span-2 text-center">Qty</div>
                      <div className="col-span-4 text-right">Total</div>
                    </div>
                    {lastSaleReceipt.items.map((item: any) => (
                      <div key={item.product.id} className="grid grid-cols-12 text-slate-700 font-mono">
                        <div className="col-span-6 truncate">{item.product.name}</div>
                        <div className="col-span-2 text-center">x{item.quantity}</div>
                        <div className="col-span-4 text-right">Rs. {(item.product.selling_price * item.quantity).toLocaleString()}</div>
                      </div>
                    ))}
                  </>
                )}
              </div>

              <div className="border-t border-dashed border-slate-300 mt-4 pt-3 text-right">
                <div className="text-xs text-slate-600">Subtotal: Rs. {lastSaleReceipt.total.toLocaleString()}</div>
                <div className="font-bold text-sm text-slate-900 mt-1">Kul Total: Rs. {lastSaleReceipt.total.toLocaleString()}</div>
              </div>

              <div className="text-center text-[10px] text-slate-400 mt-8 border-t pt-3">
                Shukriya! Visit Again.
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6 print:hidden">
              <button
                onClick={() => window.print()}
                className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center gap-2 transition"
              >
                <Printer className="w-4 h-4" /> Print Raseed
              </button>
            </div>
          </div>
        </div>
      )}
      {/* MODAL 5: LOW STOCK PURCHASE ORDER SHEET */}
      {showOrderModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl p-6 space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="font-bold text-lg text-white">
                {lang === "ur" ? "کم سٹاک آرڈر شیٹ (خریداری رپورٹ)" : "Low Stock Order Sheet (Purchase Plan)"}
              </h3>
              <button onClick={() => setShowOrderModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {(() => {
                const lowStock = products.filter(p => p.stock_quantity <= p.reorder_level);
                if (lowStock.length === 0) {
                  return (
                    <div className="text-center text-slate-500 py-8 text-sm">
                      {lang === "ur" ? "سب مال پورا ہے! کوئی چیز شارٹ نہیں ہے۔" : "All stock levels healthy! No items need reordering."}
                    </div>
                  );
                }

                const grouped: { [key: string]: typeof lowStock } = {};
                lowStock.forEach(p => {
                  const sName = contacts.find(c => c.id === p.supplier_id)?.name || "General Supplier / Other";
                  if (!grouped[sName]) grouped[sName] = [];
                  grouped[sName].push(p);
                });

                return Object.keys(grouped).map(supplier => (
                  <div key={supplier} className="bg-slate-950/40 border border-slate-850 p-4 rounded-xl space-y-3">
                    <h4 className="font-bold text-sm text-emerald-400 border-b border-slate-800 pb-1.5">{supplier}</h4>
                    <div className="space-y-2">
                      {grouped[supplier].map(p => (
                        <div key={p.id} className="flex justify-between text-xs text-slate-300">
                          <span>{p.name} ({p.sku})</span>
                          <span className="font-mono text-rose-450 font-semibold">
                            {lang === "ur" ? `موجودہ سٹاک: ${p.stock_quantity}` : `Current Stock: ${p.stock_quantity}`} (Min: {p.reorder_level})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ));
              })()}
            </div>

            <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowOrderModal(false)}
                className="px-4 py-2 border border-slate-800 text-slate-400 text-xs font-semibold rounded-lg hover:text-white"
              >
                {lang === "ur" ? "بند کریں" : "Close"}
              </button>
              <button
                type="button"
                onClick={copyOrderSheet}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg transition"
              >
                {lang === "ur" ? "واٹس ایپ کاپی کریں" : "Copy Order List"}
              </button>
            </div>
          </div>
        </div>
      )}
      {/* MODAL 6: PRICE HISTORY */}
      {showPriceHistoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-6 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <h3 className="font-bold text-lg text-white">
                {lang === "ur" ? `قیمت کی تبدیلی کی تفصیل: ${historyProductName}` : `Price History: ${historyProductName}`}
              </h3>
              <button onClick={() => setShowPriceHistoryModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {priceHistory.length === 0 ? (
                <div className="text-center text-slate-500 py-6 text-xs">
                  {lang === "ur" ? "قیمت میں کوئی تبدیلی ریکارڈ نہیں کی گئی۔" : "No price changes recorded for this item."}
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-350">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                        <th className="py-2">{lang === "en" ? "Date" : "تاریخ"}</th>
                        <th className="py-2 text-right">{lang === "en" ? "Old Price" : "پرانی قیمت"}</th>
                        <th className="py-2 text-right">{lang === "en" ? "New Price" : "نئی قیمت"}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {priceHistory.map((h, idx) => (
                        <tr key={idx} className="border-b border-slate-850 hover:bg-slate-900/15">
                          <td className="py-2.5 font-mono text-slate-500">{h.change_date}</td>
                          <td className="py-2.5 text-right font-mono text-slate-400">Rs. {h.old_price.toLocaleString()}</td>
                          <td className="py-2.5 text-right font-mono text-emerald-450 font-bold">Rs. {h.new_price.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="border-t border-slate-800 pt-4 flex justify-end">
              <button
                type="button"
                onClick={() => setShowPriceHistoryModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg"
              >
                {lang === "ur" ? "بند کریں" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
