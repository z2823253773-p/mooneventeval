struct Counts { fn : Int }
test "old field" { let c : Counts = { fn: 2 }; inspect(c.fn, content="2") }
