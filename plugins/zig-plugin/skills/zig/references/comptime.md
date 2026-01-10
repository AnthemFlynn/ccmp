# Comptime Deep Dive

Zig's compile-time evaluation is one of its most powerful features. Unlike macros, comptime code is the same language as runtime code, just evaluated at compile time.

## Comptime Fundamentals

### When Code Runs at Comptime

```zig
// 1. `comptime` keyword forces compile-time evaluation
const hash = comptime computeHash("static string");

// 2. Generic type parameters are always comptime
fn GenericFn(comptime T: type) type { ... }

// 3. Array sizes must be comptime-known
const arr: [comptime_known_size]u8 = undefined;

// 4. comptime blocks
const value = comptime {
    var x: u32 = 0;
    for ("hello") |c| x += c;
    break :blk x;
};
```

### Type as First-Class Value

```zig
fn printType(comptime T: type) void {
    const info = @typeInfo(T);
    switch (info) {
        .Struct => |s| {
            inline for (s.fields) |field| {
                std.debug.print("field: {s}\n", .{field.name});
            }
        },
        .Int => |i| {
            std.debug.print("int: {d} bits, signed: {}\n", .{ i.bits, i.signedness == .signed });
        },
        else => std.debug.print("other type\n", .{}),
    }
}
```

## Type Construction Patterns

### Generic Container

```zig
pub fn ArrayList(comptime T: type) type {
    return struct {
        items: Slice,
        capacity: usize,
        allocator: Allocator,

        const Self = @This();
        const Slice = []T;

        pub fn init(allocator: Allocator) Self {
            return .{
                .items = &[_]T{},
                .capacity = 0,
                .allocator = allocator,
            };
        }

        pub fn append(self: *Self, item: T) !void {
            if (self.items.len >= self.capacity) {
                try self.ensureCapacity(self.items.len + 1);
            }
            self.items.len += 1;
            self.items[self.items.len - 1] = item;
        }

        pub fn deinit(self: *Self) void {
            if (self.capacity > 0) {
                self.allocator.free(self.items.ptr[0..self.capacity]);
            }
        }
    };
}
```

### Tagged Union from Enum

```zig
fn EnumVariant(comptime E: type) type {
    const info = @typeInfo(E).Enum;
    
    var fields: [info.fields.len]std.builtin.Type.UnionField = undefined;
    for (info.fields, 0..) |field, i| {
        fields[i] = .{
            .name = field.name,
            .type = void,  // or derive from field
            .alignment = 0,
        };
    }
    
    return @Type(.{
        .Union = .{
            .layout = .auto,
            .tag_type = E,
            .fields = &fields,
            .decls = &.{},
        },
    });
}
```

### Mixin Pattern

```zig
fn Comparable(comptime Self: type) type {
    return struct {
        pub fn lessThanOrEqual(self: Self, other: Self) bool {
            return !other.lessThan(self);
        }
        
        pub fn greaterThan(self: Self, other: Self) bool {
            return other.lessThan(self);
        }
        
        pub fn greaterThanOrEqual(self: Self, other: Self) bool {
            return !self.lessThan(other);
        }
    };
}

const MyInt = struct {
    value: i32,
    
    pub fn lessThan(self: MyInt, other: MyInt) bool {
        return self.value < other.value;
    }
    
    // Import mixin methods
    pub usingnamespace Comparable(MyInt);
};
```

## @typeInfo and @Type

### Inspecting Types

```zig
fn inspectStruct(comptime T: type) void {
    const info = @typeInfo(T);
    if (info != .Struct) @compileError("Expected struct type");
    
    const struct_info = info.Struct;
    
    // Access struct properties
    _ = struct_info.layout;      // .auto, .@"extern", .@"packed"
    _ = struct_info.fields;      // Array of field info
    _ = struct_info.decls;       // Declarations (functions, consts)
    _ = struct_info.is_tuple;    // Is this a tuple struct?
}

fn getFieldNames(comptime T: type) []const []const u8 {
    const fields = @typeInfo(T).Struct.fields;
    var names: [fields.len][]const u8 = undefined;
    for (fields, 0..) |field, i| {
        names[i] = field.name;
    }
    return &names;
}
```

### Constructing Types

```zig
fn StructWithFields(comptime field_names: []const []const u8) type {
    // Use comptime block to ensure fields array has static lifetime
    comptime {
        var fields: [field_names.len]std.builtin.Type.StructField = undefined;
        
        for (field_names, 0..) |name, i| {
            fields[i] = .{
                .name = name,
                .type = []const u8,
                .default_value = null,
                .is_comptime = false,
                .alignment = 0,
            };
        }
        
        return @Type(.{
            .Struct = .{
                .layout = .auto,
                .fields = &fields,  // Safe: comptime block gives static lifetime
                .decls = &.{},
                .is_tuple = false,
            },
        });
    }
}

// Usage:
const MyStruct = StructWithFields(&.{ "name", "value", "count" });
// MyStruct has fields: name, value, count - all []const u8
```

## Compile-Time Algorithms

### String Operations

```zig
fn comptimeConcat(comptime strings: []const []const u8) []const u8 {
    comptime {
        var len: usize = 0;
        for (strings) |s| len += s.len;
        
        var result: [len]u8 = undefined;
        var pos: usize = 0;
        for (strings) |s| {
            @memcpy(result[pos..][0..s.len], s);
            pos += s.len;
        }
        return &result;
    }
}

fn comptimeSplit(comptime str: []const u8, comptime delim: u8) []const []const u8 {
    comptime {
        var count: usize = 1;
        for (str) |c| if (c == delim) count += 1;
        
        var result: [count][]const u8 = undefined;
        var start: usize = 0;
        var i: usize = 0;
        
        for (str, 0..) |c, pos| {
            if (c == delim) {
                result[i] = str[start..pos];
                i += 1;
                start = pos + 1;
            }
        }
        result[i] = str[start..];
        return &result;
    }
}
```

### Compile-Time Hashing

```zig
fn comptimeHash(comptime str: []const u8) u64 {
    comptime {
        // FNV-1a hash
        var hash: u64 = 0xcbf29ce484222325;
        for (str) |byte| {
            hash ^= byte;
            hash *%= 0x100000001b3;
        }
        return hash;
    }
}

// Perfect hash table generation
fn PerfectHashMap(comptime keys: []const []const u8, comptime V: type) type {
    const n = keys.len;
    
    return struct {
        values: [n]V,
        
        pub fn get(self: *const @This(), key: []const u8) ?V {
            const hash = comptimeHash(key);
            const idx = hash % n;
            
            // Verify key matches (comptime-generated check)
            inline for (keys, 0..) |k, i| {
                if (idx == i and std.mem.eql(u8, key, k)) {
                    return self.values[i];
                }
            }
            return null;
        }
    };
}
```

## Inline For and Switch

### Unrolled Iteration

```zig
fn sumFields(comptime T: type, value: T) i64 {
    var sum: i64 = 0;
    
    inline for (@typeInfo(T).Struct.fields) |field| {
        const field_value = @field(value, field.name);
        if (@typeInfo(field.type) == .Int) {
            sum += @as(i64, field_value);
        }
    }
    
    return sum;
}
```

### Type-Based Dispatch

```zig
fn serialize(value: anytype) ![]u8 {
    const T = @TypeOf(value);
    
    return switch (@typeInfo(T)) {
        .Int => try serializeInt(value),
        .Float => try serializeFloat(value),
        .Pointer => |ptr| {
            if (ptr.size == .Slice and ptr.child == u8) {
                return try serializeString(value);
            }
            @compileError("Unsupported pointer type");
        },
        .Struct => try serializeStruct(value),
        else => @compileError("Unsupported type: " ++ @typeName(T)),
    };
}
```

## Common Comptime Patterns

### Configuration Struct

```zig
pub const Config = struct {
    buffer_size: usize = 4096,
    max_connections: usize = 100,
    enable_logging: bool = true,
    
    pub fn validate(comptime self: Config) void {
        if (self.buffer_size < 64) {
            @compileError("buffer_size must be at least 64");
        }
        if (self.max_connections == 0) {
            @compileError("max_connections must be > 0");
        }
    }
};

pub fn Server(comptime config: Config) type {
    comptime config.validate();
    
    return struct {
        buffer: [config.buffer_size]u8 = undefined,
        // ...
    };
}
```

### Format String Parsing

```zig
fn formatParser(comptime fmt: []const u8) type {
    comptime {
        var arg_count: usize = 0;
        var i: usize = 0;
        while (i < fmt.len) : (i += 1) {
            if (fmt[i] == '{' and i + 1 < fmt.len and fmt[i + 1] == '}') {
                arg_count += 1;
                i += 1;
            }
        }
        
        return struct {
            pub const expected_args = arg_count;
            
            pub fn format(args: anytype) []const u8 {
                if (args.len != expected_args) {
                    @compileError("Wrong number of arguments");
                }
                // ... format implementation
            }
        };
    }
}
```

## Comptime Gotchas

### Variables Must Be Const

```zig
// WRONG: Can't have runtime-mutable comptime
comptime var x: u32 = 0;  // This IS allowed during comptime block...
x += 1;  // ... but can't mutate at runtime

// CORRECT: Result is const
const x = comptime blk: {
    var tmp: u32 = 0;
    tmp += 1;
    break :blk tmp;
};
```

### No Runtime Values in Comptime

```zig
// WRONG
fn bad(runtime_val: usize) type {
    return [runtime_val]u8;  // Can't use runtime value for array size
}

// CORRECT: Use slices or comptime param
fn good(comptime size: usize) type {
    return [size]u8;
}

fn also_good(allocator: Allocator, runtime_size: usize) ![]u8 {
    return allocator.alloc(u8, runtime_size);
}
```

### Comptime Pointers

```zig
// WRONG: Comptime pointer to runtime memory
fn bad() *const u8 {
    const s = "hello";
    return comptime &s[0];  // Pointer to runtime string
}

// CORRECT: Comptime pointer to comptime data
fn good() *const u8 {
    comptime {
        const s = "hello";
        return &s[0];
    }
}
```
