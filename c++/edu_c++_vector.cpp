#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {

    // объявление вектора
    vector<int> arr;
    vector<int> arr3(5, 1);   // из 5 элементов (начальное значение 1)

    // добавление элементов
    for (int i = 1; i <= 10; ++i) {
        arr.push_back(i);
    }
    
    // arr.size() - кол-во элементов
    for (int j = 0; j < arr.size(); ++j) {
        cout << arr[j] << endl;
    }

    // обход
    for (auto x: arr) {
        cout << x << endl;
    }

    cout << arr.back() << endl; // последний элемент

    arr.pop_back(); // удалить последний элемент 

    sort(arr.begin(), arr.end()); // сортировка  
    reverse(arr.begin(), arr.end()); // в обратном

    cout << *arr.begin() << endl;  // первый элемент


    vector<int> arr2{3, 5, 7, 9, 12, 14, 16};

    auto a = lower_bound(arr2.begin(), arr2.end(), 3);  // получить итератор на первый элемент отсортированного вектора значение которого не меньше 3
    auto b = upper_bound(arr2.begin(), arr2.end(), 3);  // получить итератор на первый элемент отсортированного вектора значение которого не больше 3

    cout << *a << endl << *b << endl;

    return 0;
}