from __init__ import judge, main
import threading
import time
import subprocess
import unittest
import xmlrpc.client



PORT = 8000


class ProductTestCase(unittest.TestCase):
    def test_CE(self):
        self.assertEqual(judge('', [], 0, True), 'CE')

    def test_AC(self):
        self.assertEqual(judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    return 0;\n}\n', [('1 1', '1')])[0], ['AC'])

    def test_WA(self):
        self.assertEqual(judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    return 0;\n}\n', [('2 2', '4')])[0], ['WA'])

    def test_TLE(self):
        self.assertEqual(judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    while (true)\n        ;\n    return 0;\n}\n', [('1 1', '1')], .1), (['TLE'], [100]))

    def test_RE(self):
        self.assertEqual(judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    return 0;\n}\n', [('1 0', '0')])[0], ['RE'])

    def test_case(self):
        self.assertEqual(judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    return 0;\n}\n', [('1 1', '1'), ('2 2', '4'), ('1 0', '0')])[0], ['AC', 'WA', 'RE'])

    def test_threading(self):
        t = time.time()
        judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    while (true)\n        ;\n    return 0;\n}\n', [('1 1', '1')] * 10, .1)
        self.assertAlmostEqual(time.time() - t, .1, 0)

    def test_server(self):
        threading.Thread(target=main, kwargs={'port': PORT, 'quiet': True}, daemon=True).start()
        # time.sleep(.1)
        self.assertEqual(xmlrpc.client.ServerProxy('http://127.0.0.1:' + str(PORT)).judge('#include <cstdio>\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d", a / b);\n    return 0;\n}\n', [('1 1', '1')])[0], ['AC'])

    def test_with_PyLint(self):
        pylint = subprocess.run(['pylint', '-sn', '.'], capture_output=True).stdout.decode()
        self.assertFalse(pylint, '\n' + pylint)


if __name__ == '__main__':
    unittest.main()
