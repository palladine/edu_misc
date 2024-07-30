#include <iostream>
#include <algorithm>
#include <set>
#include <map>
#include <unordered_map>

using namespace std;

int main() {

    // O(log n)
    map<string,int> m;
    m["monkey"] = 4;
    m["banana"] = 3;
    m["harpsichord"] = 9;
    cout << m["banana"] << endl;

    for (auto x : m) {
        cout << x.first << " " << x.second << endl;
    }



    // O(1) !
    unordered_map<string, int> um;
    um["monkey"] = 4;
    um["banana"] = 3;
    um["harpsichord"] = 9;
    cout << um["banana"] << endl;

    for (auto x : um) {
        cout << x.first << " " << x.second << endl;
    }

    return 0;
}