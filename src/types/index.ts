export interface User {
  id: number
  username: string
  email: string
  role: 'customer' | 'artisan' | 'admin'
  phone?: string
  avatar_url?: string
  created_at: string
}

export interface Product {
  id: number
  name: string
  description?: string
  category: 'wedding' | 'enterprise' | 'festival' | 'custom'
  template_image_url?: string
  price_base: number
  is_template: boolean
  stock: number
  version: number
  created_at: string
  images: ProductImage[]
}

export interface ProductListItem {
  id: number
  name: string
  category: string
  template_image_url?: string
  price_base: number
  is_template: boolean
  stock: number
}

export interface ProductImage {
  id: number
  product_id: number
  image_url: string
  sort_order: number
}

export interface Order {
  id: number
  order_no: string
  customer_id: number
  product_id: number
  status: 'pending' | 'assigned' | 'in_progress' | 'qc' | 'shipped' | 'awaiting_review' | 'completed' | 'cancelled'
  total_price: number
  custom_size?: string
  custom_color?: string
  custom_message?: string
  reference_image_url?: string
  is_original: boolean
  version: number
  created_at: string
  updated_at: string
  assignments: OrderAssignment[]
  progress_photos: ProgressPhoto[]
}

export interface OrderAssignment {
  id: number
  order_id: number
  artisan_id: number
  assigned_at: string
  deadline?: string
}

export interface ProgressPhoto {
  id: number
  order_id: number
  uploaded_by: number
  image_url: string
  description?: string
  uploaded_at: string
}

export interface Artisan {
  id: number
  user_id: number
  name: string
  specialty?: string
  monthly_capacity: number
  bio?: string
  avatar_url?: string
  average_rating: number
  review_count: number
}

export interface Review {
  id: number
  order_id: number
  product_id: number
  artisan_id: number
  customer_id: number
  rating: number
  comment?: string
  created_at: string
  customer_name?: string
}

export interface ReviewCreate {
  rating: number
  comment?: string
}

export interface ArtisanSchedule {
  id: number
  artisan_id: number
  year_month: number
  assigned_count: number
  capacity: number
  version: number
}

export interface ArtisanTask {
  order_id: number
  order_no: string
  status: string
  assigned_at: string
  deadline?: string
}

export interface Notification {
  id: number
  user_id: number
  title: string
  content?: string
  type: string
  is_read: boolean
  created_at: string
}
