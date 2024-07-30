#include <iostream>
#include <vector>
#include <algorithm>
#include <deque>

using namespace std;

int main() {
// O(1)
    deque<int> dq;
    dq.push_back(5);
    dq.push_front(7);

    dq.pop_back();
    dq.pop_front();

    return 0;
}