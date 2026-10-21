///|
// Temporary until T3 constructs the task-wide budget.
#warnings("-struct_never_constructed")
priv struct WorkBudget {
  mut used : Int64
  limit : Int64
}

///|
// Temporary until T3 evaluation consumes all fields in production.
#warnings("-unused_field")
priv struct Matching {
  pairs : Array[(Int, Int)]
  reference_degree : Array[Int]
  prediction_degree : Array[Int]
  steps : Int64
  adjacency_checks : Int64
}

///|
fn consume_step(budget : WorkBudget) -> Result[Unit, EvalError] {
  if budget.used >= budget.limit {
    Err({
      kind: Resource,
      code: "RESOURCE_LIMIT",
      message: "Matching work budget exhausted",
      path: Some("work.matching_steps"),
      limit: Some(budget.limit),
      observed: Some(budget.used + 1L),
    })
  } else {
    budget.used = budget.used + 1L
    Ok(())
  }
}

///|
// Input rows are strictly ascending, unique and in range (T3 graph builder).
// No recursion: DFS frames retain the next edge and the path's incoming prediction.
// Temporary until T3 evaluation calls this internal API.
#warnings("-unused_value")
fn maximum_matching(
  adjacency : Array[Array[Int]],
  prediction_count : Int,
  budget : WorkBudget,
) -> Result[Matching, EvalError] {
  let initial_steps = budget.used
  let reference_count = adjacency.length()
  let reference_match = Array::make(reference_count, -1)
  let prediction_match = Array::make(prediction_count, -1)
  let reference_degree = Array::makei(reference_count, r => {
    adjacency[r].length()
  })
  let prediction_degree = Array::make(prediction_count, 0)
  // Graph bookkeeping is O(E), distinct from charged search edge inspections.
  for row in adjacency {
    for p in row {
      prediction_degree[p] = prediction_degree[p] + 1
    }
  }
  let mut adjacency_checks = 0L
  for root in 0..<reference_count {
    match consume_step(budget) {
      Err(error) => return Err(error)
      Ok(_) => ()
    }
    // This fast path does not prevent later roots from moving this match.
    for p in adjacency[root] {
      match consume_step(budget) {
        Err(error) => return Err(error)
        Ok(_) => ()
      }
      adjacency_checks = adjacency_checks + 1L
      if true {
        match consume_step(budget) {
          Err(error) => return Err(error)
          Ok(_) => ()
        }
        reference_match[root] = p
        prediction_match[p] = root
        break
      }
    }
    if reference_match[root] != -1 {
      continue
    }
    let visited = Array::make(prediction_count, false)
    let stack : Array[Int] = [root]
    let next_edge : Array[Int] = [0]
    let incoming : Array[Int] = [-1]
    let mut augmented = false
    while !stack.is_empty() && !augmented {
      let top = stack.length() - 1
      let r = stack[top]
      let edge = next_edge[top]
      if edge >= adjacency[r].length() {
        ignore(stack.pop())
        ignore(next_edge.pop())
        ignore(incoming.pop())
        continue
      }
      match consume_step(budget) {
        Err(error) => return Err(error)
        Ok(_) => ()
      }
      adjacency_checks = adjacency_checks + 1L
      let p = adjacency[r][edge]
      next_edge[top] = edge + 1
      if visited[p] {
        continue
      }
      visited[p] = true
      let owner = prediction_match[p]
      if owner == -1 {
        // Rewire the full path backwards; errors expose no partially changed graph.
        let mut target = p
        let mut depth = top
        while depth >= 0 {
          match consume_step(budget) {
            Err(error) => return Err(error)
            Ok(_) => ()
          }
          let reference = stack[depth]
          reference_match[reference] = target
          prediction_match[target] = reference
          target = incoming[depth]
          depth = depth - 1
        }
        augmented = true
      } else {
        match consume_step(budget) {
          Err(error) => return Err(error)
          Ok(_) => ()
        }
        stack.push(owner)
        next_edge.push(0)
        incoming.push(p)
      }
    }
  }
  let pairs : Array[(Int, Int)] = []
  for r in 0..<reference_count {
    if reference_match[r] != -1 {
      pairs.push((r, reference_match[r]))
    }
  }
  Ok({
    pairs,
    reference_degree,
    prediction_degree,
    steps: budget.used - initial_steps,
    adjacency_checks,
  })
}
