import { Dessert } from '../types';
import { getImageUrl } from '../utils/image';

interface DessertModalProps {
  dessert: Dessert;
  onClose: () => void;
}

export default function DessertModal({ dessert, onClose }: DessertModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Заголовок */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">{dessert.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Контент */}
        <div className="p-6 space-y-6">
          {/* Изображение */}
          {dessert.image_url && (
            <div className="w-full h-64 bg-gray-200 rounded-lg overflow-hidden">
              <img
                src={getImageUrl(dessert.image_url) || ''}
                alt={dessert.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            </div>
          )}

          {/* Категория */}
          <div>
            <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {dessert.category}
            </span>
          </div>

          {/* Описание */}
          {dessert.description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Описание</h3>
              <p className="text-gray-700 leading-relaxed">{dessert.description}</p>
            </div>
          )}

          {/* Состав */}
          {dessert.ingredients && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Ingredients</h3>
              <p className="text-gray-700 leading-relaxed">{dessert.ingredients}</p>
            </div>
          )}

          {/* КБЖУ */}
          {(dessert.calories || dessert.proteins || dessert.fats || dessert.carbs) && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Nutrition (per 100g)</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {dessert.calories !== null && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Calories</div>
                    <div className="text-xl font-bold text-gray-900">{dessert.calories.toFixed(1)} kcal</div>
                  </div>
                )}
                {dessert.proteins !== null && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Proteins</div>
                    <div className="text-xl font-bold text-gray-900">{dessert.proteins.toFixed(1)} g</div>
                  </div>
                )}
                {dessert.fats !== null && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Fats</div>
                    <div className="text-xl font-bold text-gray-900">{dessert.fats.toFixed(1)} g</div>
                  </div>
                )}
                {dessert.carbs !== null && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Carbs</div>
                    <div className="text-xl font-bold text-gray-900">{dessert.carbs.toFixed(1)} g</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Вес/Фасовка */}
          {dessert.weight && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Weight/Packaging</h3>
              <p className="text-gray-700">{dessert.weight}</p>
            </div>
          )}

          {/* Стоимость */}
          {dessert.price !== null && dessert.price !== undefined && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Price</h3>
              <p className="text-2xl font-bold text-blue-600">{dessert.price.toFixed(2)} THB</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

