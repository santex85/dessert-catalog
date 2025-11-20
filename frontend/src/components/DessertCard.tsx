import { Dessert } from '../types';
import { getImageUrl } from '../utils/image';

interface DessertCardProps {
  dessert: Dessert;
  isSelected: boolean;
  onSelect: () => void;
  onClick: () => void;
}

export default function DessertCard({ dessert, isSelected, onSelect, onClick }: DessertCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 relative group cursor-pointer"
      onClick={onClick}
    >
      {/* Чекбокс для выбора */}
      <div
        className="absolute top-2 right-2 z-10"
        onClick={(e) => {
          e.stopPropagation();
          onSelect();
        }}
      >
        <div
          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
            isSelected
              ? 'bg-blue-600 border-blue-600'
              : 'bg-white border-gray-300 group-hover:border-blue-400'
          }`}
        >
          {isSelected && (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>

      {/* Изображение */}
      <div className="h-48 bg-gray-200 overflow-hidden">
        {dessert.image_url ? (
          <img
            src={getImageUrl(dessert.image_url) || ''}
            alt={dessert.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            onError={(e) => {
              // Если изображение не загрузилось, показываем placeholder
              e.currentTarget.style.display = 'none';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Информация */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
          {dessert.title}
        </h3>
        <p className="text-sm text-gray-500 mb-2">{dessert.category}</p>
        {dessert.description && (
          <p className="text-sm text-gray-600 line-clamp-2">{dessert.description}</p>
        )}
        <div className="flex justify-between items-center mt-2">
          {dessert.weight && (
            <p className="text-xs text-gray-400">Weight: {dessert.weight}</p>
          )}
          {dessert.price !== null && dessert.price !== undefined && (
            <p className="text-lg font-bold text-blue-600">{dessert.price.toFixed(2)} ₽</p>
          )}
        </div>
      </div>

      {/* Кнопка "Подробнее" при наведении */}
      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
        <span className="text-white font-medium bg-blue-600 px-4 py-2 rounded-lg">
          Details
        </span>
      </div>
    </div>
  );
}

