// credit goes to: https://oj.uz/submission/115679
// apologize my bad code style


#include "combo.h"
#include <bits/stdc++.h>
    
using namespace std;
    
string guess_sequence(int N) {
    int x;
    string s;
    char ch[4]= {'A', 'B', 'X', 'Y'};
    if (press("AB") >= 1) x = press("A") != 1;
    else x = 2 + (press("X") < 1);
    s += ch[x];
    if (N == 1) return s;
    swap(ch[x], ch[3]);
    for (int i = 1; i < N - 1; i++) {
        x = press(s + ch[0] + ch[0] + s + ch[0] + ch[1] + s + ch[0] + ch[2] + s + ch[1]);
        if (x == i + 2) s+=ch[0];
        else if (x == i + 1) s+=ch[1];
        else s += ch[2];
    }
    if (press(s + ch[0] + s + ch[1]) == N) {
        if (press(s + ch[0]) == N) s += ch[0];
        else s += ch[1];
    } else s += ch[2];
    return s;
}