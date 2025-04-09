// math_contract.java
public class MathContract {
    public static void main() {
        int a = 10;
        int b = 4;
        
        // Arithmetic
        int add = a + b;      // 13
        int sub = a - b;      // 7
        int mul = a * b;      // 30
        int div = a / b;      // 3
        int mod = a % b;      // 1
        
        // Comparisons
        int lt = a < b;       // 0
        int gt = a > b;       // 1
        int eq = a == b;      // 0
        int neq = a != b;     // 1
        int lte = a <= b;     // 0
        int gte = a >= b;     // 1
        
        // Zero checks
        int zero = 0;
        int isZero = !zero;   // 1
        int notZero = !a;      // 0
    }
}
