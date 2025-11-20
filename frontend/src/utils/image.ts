/**
 * Утилита для работы с изображениями
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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

  // Если это локальный путь, начинающийся с /, возвращаем как есть
  // Nginx проксирует /static на backend, поэтому относительные пути работают
  if (imageUrl.startsWith('/')) {
    return imageUrl;
  }

  // Иначе считаем, что это относительный путь - добавляем базовый URL только если он задан
  if (API_BASE_URL) {
    return `${API_BASE_URL}/${imageUrl}`;
  }
  
  return `/${imageUrl}`;
}

