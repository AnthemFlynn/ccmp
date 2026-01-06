# Allocators Deep Dive

Zig's explicit allocator model is its most distinctive feature. Understanding allocator selection, composition, and patterns is essential for effective Zig development.

## Allocator Types

### GeneralPurposeAllocator (GPA)

**Use for**: Development, debugging, applications where safety > performance

```zig
var gpa = std.heap.GeneralPurposeAllocator(.{
    .safety = true,                    // Enable safety checks (default: true in Debug)
    .thread_safe = true,               // Multi-threaded access (default: true)
    .enable_memory_limit = false,      // Track total allocation size
    .stack_trace_frames = 8,           // Stack frames in leak reports
}){};
defer {
    const check = gpa.deinit();
    if (check == .leak) {
        std.log.err("Memory leak detected!", .{});
    }
}
const allocator = gpa.allocator();
```

**Safety features**:
- Use-after-free detection (fills freed memory with 0xAA)
- Double-free detection
- Memory leak reporting on deinit
- Buffer overflow detection (guard pages in some modes)

### ArenaAllocator

**Use for**: Request handling, parsing, batch operations - anything with a clear "done" point

```zig
var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
defer arena.deinit();  // Frees everything at once

const allocator = arena.allocator();

// Allocate freely - no need for individual frees
const data = try allocator.alloc(u8, 1000);
const more = try allocator.alloc(u32, 500);
// ... work with data ...
// All freed when arena.deinit() is called
```

**Pattern: Request-scoped arena**:
```zig
fn handleRequest(permanent_allocator: Allocator, request: Request) !Response {
    var arena = std.heap.ArenaAllocator.init(permanent_allocator);
    defer arena.deinit();
    
    const scratch = arena.allocator();
    
    // All temporary allocations use scratch
    const parsed = try parseBody(scratch, request.body);
    const validated = try validate(scratch, parsed);
    
    // Only the response is allocated from permanent allocator
    return try Response.init(permanent_allocator, validated);
}
```

### FixedBufferAllocator

**Use for**: Stack allocation, embedded, known-size buffers

```zig
var buffer: [4096]u8 = undefined;
var fba = std.heap.FixedBufferAllocator.init(&buffer);
const allocator = fba.allocator();

// No heap allocation - uses the stack buffer
const data = try allocator.alloc(u8, 100);
```

**Pattern: Stack-based parsing**:
```zig
fn parseSmallJson(input: []const u8) !Value {
    var buffer: [8192]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    
    return std.json.parseFromSlice(Value, fba.allocator(), input, .{});
}
```

### c_allocator

**Use for**: Production performance, C library interop

```zig
const allocator = std.heap.c_allocator;
// Uses malloc/free - fast, no safety checks
```

### page_allocator

**Use for**: Large allocations, memory-mapped regions

```zig
const allocator = std.heap.page_allocator;
// Allocates directly from OS - page-aligned, large minimum size
```

## Allocator Composition

### Logging Allocator

```zig
var gpa = std.heap.GeneralPurposeAllocator(.{}){};
var logging = std.heap.loggingAllocator(gpa.allocator());
const allocator = logging.allocator();

// Every alloc/free is logged with size and address
```

### Scoped Allocators (Passing Down)

```zig
const Server = struct {
    allocator: Allocator,
    connections: std.ArrayList(Connection),
    
    pub fn init(allocator: Allocator) Server {
        return .{
            .allocator = allocator,
            .connections = std.ArrayList(Connection).init(allocator),
        };
    }
    
    pub fn addConnection(self: *Server, socket: Socket) !void {
        // Uses stored allocator
        try self.connections.append(try Connection.init(self.allocator, socket));
    }
};
```

## Custom Allocators

### Interface Implementation

```zig
const MyAllocator = struct {
    // Required state
    backing: Allocator,
    stats: AllocationStats,
    
    pub fn allocator(self: *MyAllocator) Allocator {
        return .{
            .ptr = self,
            .vtable = &.{
                .alloc = alloc,
                .resize = resize,
                .free = free,
            },
        };
    }
    
    fn alloc(ctx: *anyopaque, len: usize, ptr_align: u8, ret_addr: usize) ?[*]u8 {
        const self: *MyAllocator = @ptrCast(@alignCast(ctx));
        self.stats.alloc_count += 1;
        return self.backing.rawAlloc(len, ptr_align, ret_addr);
    }
    
    fn resize(ctx: *anyopaque, buf: []u8, buf_align: u8, new_len: usize, ret_addr: usize) bool {
        // ... 
    }
    
    fn free(ctx: *anyopaque, buf: []u8, buf_align: u8, ret_addr: usize) void {
        // ...
    }
};
```

### Pool Allocator Pattern

```zig
fn PoolAllocator(comptime T: type) type {
    return struct {
        free_list: ?*Node,
        backing: Allocator,
        
        const Node = struct {
            data: T,
            next: ?*Node,
        };
        
        const Self = @This();
        
        pub fn acquire(self: *Self) !*T {
            if (self.free_list) |node| {
                self.free_list = node.next;
                return &node.data;
            }
            const node = try self.backing.create(Node);
            return &node.data;
        }
        
        pub fn release(self: *Self, ptr: *T) void {
            const node: *Node = @fieldParentPtr("data", ptr);
            node.next = self.free_list;
            self.free_list = node;
        }
    };
}
```

## Testing Allocators

### std.testing.allocator

```zig
test "my function allocates correctly" {
    const result = try myFunction(std.testing.allocator);
    defer std.testing.allocator.free(result);
    
    try std.testing.expect(result.len == 42);
}
// Test automatically fails if any allocation leaks
```

### FailingAllocator for Error Paths

```zig
test "handles allocation failure" {
    var failing = std.testing.FailingAllocator.init(std.testing.allocator, .{
        .fail_index = 2,  // Fail on the 3rd allocation
    });
    
    const result = myFunction(failing.allocator());
    try std.testing.expectError(error.OutOfMemory, result);
}
```

## Common Mistakes

### Mistake 1: Creating allocator in wrong scope

```zig
// WRONG: arena destroyed while data still in use
fn bad() ![]u8 {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();  // Frees the returned data!
    return try arena.allocator().alloc(u8, 100);
}

// CORRECT: caller provides allocator
fn good(allocator: Allocator) ![]u8 {
    return try allocator.alloc(u8, 100);
}
```

### Mistake 2: Mixing allocators

```zig
// WRONG: freeing with different allocator
const data = try allocator_a.alloc(u8, 100);
allocator_b.free(data);  // Undefined behavior!

// CORRECT: store allocator with allocation
const DataOwned = struct {
    allocator: Allocator,
    data: []u8,
    
    pub fn deinit(self: DataOwned) void {
        self.allocator.free(self.data);
    }
};
```

### Mistake 3: Forgetting errdefer

```zig
// WRONG: leaks on error
fn leaky(allocator: Allocator) !Thing {
    const a = try allocator.alloc(u8, 100);
    const b = try allocator.alloc(u8, 100);  // If this fails, a leaks!
    return Thing{ .a = a, .b = b };
}

// CORRECT: errdefer for cleanup
fn safe(allocator: Allocator) !Thing {
    const a = try allocator.alloc(u8, 100);
    errdefer allocator.free(a);
    
    const b = try allocator.alloc(u8, 100);
    errdefer allocator.free(b);
    
    return Thing{ .a = a, .b = b };
}
```
