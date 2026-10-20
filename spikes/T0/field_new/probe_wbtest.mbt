struct Counts { fn_count : Int }
test "mapped JSON key" {
  let c : Counts = { fn_count: 2 }
  let j = Json::object({"fn": Json::number(c.fn_count.to_double())})
  inspect(j.stringify(), content="{\"fn\":2}")
}
