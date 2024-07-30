#include <iostream>
#include <algorithm>
#include <set>

using namespace std;

int main() {
// O(log n)
    set<int> st;  // ! упорядоченное множество 
    st.insert(2);
    st.insert(5);
    st.insert(7);

    st.erase(2);

    auto first = st.begin();   // итератор на начало и конец
    auto last = st.end();
    last--;
    cout << *first << "..." << *last << endl;

//
    set<int> st2;
    for (int i=1; i<20; i+=2) {
        st2.insert(i);
    }

    for (auto el : st2) {
        cout << el << " ";
    }
    cout << endl;

    // В структуре set имеются функции lower_bound(x) и upper_bound(x), которые возвращают итератор на наименьший элемент множества, 
    // значение которого не меньше x или больше x соответственно. Если искомого элемента не существует, то обе функции возвращают end().
    auto a = st2.lower_bound(10);
    cout << *a << endl;

    auto b = st2.upper_bound(12);
    cout << *b << endl;

    auto c = st2.upper_bound(20);
    cout << *c << endl;



    // multiset
    multiset<int> mst;
    for (int i=1; i < 10; ++i) {
        mst.insert(i);
        mst.insert(i);
    }

    for (auto el : mst) {
        cout << el << " ";
    }
    cout << endl;



    return 0;
}