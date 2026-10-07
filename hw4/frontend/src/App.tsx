import { BrowserRouter, Route, Routes } from "react-router-dom"
import { AuthProvider } from "./auth.tsx"
import { ChatWidget } from "./components/ChatWidget.tsx"
import { Navbar } from "./components/Navbar.tsx"
import { AboutPage } from "./pages/AboutPage.tsx"
import { HomePage } from "./pages/HomePage.tsx"
import { LoginPage } from "./pages/LoginPage.tsx"
import { ProductDetailPage } from "./pages/ProductDetailPage.tsx"
import { ProductsPage } from "./pages/ProductsPage.tsx"
import { RegisterPage } from "./pages/RegisterPage.tsx"

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
        <ChatWidget />
      </AuthProvider>
    </BrowserRouter>
  )
}
