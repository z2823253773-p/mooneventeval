// Release runner executes these tests directly; timings include graph construction
// and pair-validity assertions, not compilation and not only the matching call.

///|
fn report_matching_benchmark(
  name : String,
  size : Int,
  result : Matching,
) -> Unit {
  println(
    "{\"benchmark\":\"\{name}\",\"size_each_side\":\{size},\"pairs\":\{result.pairs.length()},\"adjacency_checks\":\{result.adjacency_checks},\"steps\":\{result.steps}}",
  )
}

///|
test "matching_benchmark_complete_500" {
  let graph = Array::makei(500, _ => Array::makei(500, p => p))
  let result = check_matching(graph, 500, 500)
  inspect(result.adjacency_checks == 125_250L, content="true")
  inspect(result.steps == 126_250L, content="true")
  report_matching_benchmark("complete-500", 500, result)
}

///|
test "matching_benchmark_complete_1000" {
  let graph = Array::makei(1000, _ => Array::makei(1000, p => p))
  let result = check_matching(graph, 1000, 1000)
  inspect(result.adjacency_checks == 500_500L, content="true")
  inspect(result.steps == 502_500L, content="true")
  report_matching_benchmark("complete-1000", 1000, result)
}

///|
test "matching_benchmark_sparse_1000" {
  let result = check_matching(Array::makei(1000, r => [r]), 1000, 1000)
  inspect(result.steps == 3000L, content="true")
  report_matching_benchmark("sparse-1000", 1000, result)
}

///|
test "matching_benchmark_chain_1000" {
  let graph = Array::makei(1000, r => if r < 999 { [r, r + 1] } else { [0] })
  let result = check_matching(graph, 1000, 1000)
  inspect(result.pairs[999] == (999, 0), content="true")
  report_matching_benchmark("chain-1000", 1000, result)
}
