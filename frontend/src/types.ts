export interface Dessert {
  id: number;
  title: string;
  category: string;
  image_url: string | null;
  description: string | null;
  ingredients: string | null;
  calories: number | null;
  proteins: number | null;
  fats: number | null;
  carbs: number | null;
  weight: string | null;
  price: number | null;
  is_active: boolean;
}

export interface PDFExportSettings {
  dessert_ids: number[];
  include_ingredients: boolean;
  include_nutrition: boolean;
  include_title_page: boolean;
  company_name?: string;
  manager_contact?: string;
  logo_url?: string;
  template?: string;
}

export interface PDFTemplate {
  id: string;
  name: string;
  description: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  logo_url?: string | null;
  company_name?: string | null;
  manager_contact?: string | null;
  created_at?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
