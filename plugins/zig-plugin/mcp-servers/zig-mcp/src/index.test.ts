import { describe, test, expect } from "bun:test";
import { parseZigErrors } from "./index";

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
