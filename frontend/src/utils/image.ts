/**
 * Утилита для работы с изображениями
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Получить полный URL изображения
 * Поддерживает как локальные пути (/static/images/...), так и внешние URL
 */
export function getImageUrl(imageUrl: string | null | undefined): string | null {
  if (!imageUrl) {
    return null;
  }

  // Если это уже полный URL (http/https), возвращаем как есть
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }

  // Если это локальный путь, добавляем базовый URL API
  if (imageUrl.startsWith('/')) {
    return `${API_BASE_URL}${imageUrl}`;
  }

  // Иначе считаем, что это относительный путь
  return `${API_BASE_URL}/${imageUrl}`;
}

