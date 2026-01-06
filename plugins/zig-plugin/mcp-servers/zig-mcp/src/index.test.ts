import { describe, test, expect } from "bun:test";
import { parseZigErrors, parseZvmList } from "./index";

describe("parseZigErrors", () => {
  test("parses standard error format", () => {
    const output = "src/main.zig:10:5: error: expected ';'";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0]).toEqual({
      file: "src/main.zig",
      line: 10,
      column: 5,
      kind: "error",
      message: "expected ';'",
    });
  });

  test("parses warnings", () => {
    const output = "src/lib.zig:20:1: warning: unused variable 'x'";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].kind).toBe("warning");
    expect(errors[0].message).toBe("unused variable 'x'");
  });

  test("parses notes", () => {
    const output = "src/lib.zig:5:10: note: declared here";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].kind).toBe("note");
  });

  test("handles Windows paths", () => {
    const output = "C:\\project\\src\\main.zig:10:5: error: test error";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].file).toBe("C:\\project\\src\\main.zig");
    expect(errors[0].line).toBe(10);
    expect(errors[0].column).toBe(5);
  });

  test("handles empty output", () => {
    expect(parseZigErrors("")).toEqual([]);
  });

  test("handles output with no errors", () => {
    const output = "Build successful\nNo errors found";
    expect(parseZigErrors(output)).toEqual([]);
  });

  test("handles multiple errors", () => {
    const output = `src/a.zig:1:1: error: first error
src/b.zig:2:2: error: second error
src/c.zig:3:3: warning: a warning`;
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(3);
    expect(errors[0].file).toBe("src/a.zig");
    expect(errors[0].message).toBe("first error");
    expect(errors[1].file).toBe("src/b.zig");
    expect(errors[1].message).toBe("second error");
    expect(errors[2].kind).toBe("warning");
  });

  test("handles errors with special characters in message", () => {
    const output = "src/main.zig:5:10: error: expected ')', found '{'";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].message).toBe("expected ')', found '{'");
  });

  test("handles deep nested paths", () => {
    const output =
      "src/modules/parser/lexer/tokens.zig:100:25: error: undefined identifier";
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].file).toBe("src/modules/parser/lexer/tokens.zig");
    expect(errors[0].line).toBe(100);
    expect(errors[0].column).toBe(25);
  });

  test("ignores non-error lines in mixed output", () => {
    const output = `Building...
src/main.zig:10:5: error: undefined
    const x = y;
              ^
Compilation failed`;
    const errors = parseZigErrors(output);

    expect(errors).toHaveLength(1);
    expect(errors[0].message).toBe("undefined");
  });
});

describe("parseZvmList", () => {
  test("parses simple version list", () => {
    const output = `0.11.0
0.12.0
0.13.0`;
    const result = parseZvmList(output);

    expect(result.installed).toEqual(["0.11.0", "0.12.0", "0.13.0"]);
    expect(result.active).toBeNull();
  });

  test("identifies active version with asterisk", () => {
    const output = `0.11.0
0.12.0 *
0.13.0`;
    const result = parseZvmList(output);

    expect(result.installed).toHaveLength(3);
    expect(result.active).toBe("0.12.0");
  });

  test("identifies active version with arrow", () => {
    const output = `0.11.0
0.12.0 ←
master`;
    const result = parseZvmList(output);

    expect(result.active).toBe("0.12.0");
  });

  test("handles master/nightly versions", () => {
    const output = `0.13.0
master *`;
    const result = parseZvmList(output);

    expect(result.installed).toContain("master");
    expect(result.active).toBe("master");
  });

  test("handles empty output", () => {
    const result = parseZvmList("");

    expect(result.installed).toEqual([]);
    expect(result.active).toBeNull();
  });

  test("handles output with decorative lines", () => {
    const output = `---installed---
0.12.0
0.13.0 *
---default---`;
    const result = parseZvmList(output);

    // Should ignore lines with dashes
    expect(result.installed).toEqual(["0.12.0", "0.13.0"]);
    expect(result.active).toBe("0.13.0");
  });
});
