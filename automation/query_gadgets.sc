/* 
  joern --script query_gadgets.sc --params inputPath=/path/to/source.c
*/

import io.shiftleft.semanticcpg.language._
import io.shiftleft.codepropertygraph.generated.nodes._

import java.io.File

@main def exec(inputPath: String, outFile: String = "gadgets.json") = {
  // Determine project name from input path (basename)
  val file = new File(inputPath)
  val projectName = file.getName
  
  // Check if project already exists in workspace
  if (workspace.project(projectName).isDefined) {
    println(s"Project '$projectName' already exists. Loading CPG...")
    console.open(projectName)
  } else {
    println(s"Creating new CPG for '$inputPath'...")
    importCode(inputPath)
  }
  
  // Define Sources (Hardware I/O + PoC simplifications)
  def sources = cpg.call("gets|fgets|recv|read|scanf|fscanf|memset|fread").argument(1) ++ cpg.call("alloca|ALLOCA")
  
  // 1. Standard C Functions (memcpy, strcpy, etc.) - Destination is Argument 1
  def standardSinks = cpg.call("memcpy|strcpy|strncpy|sprintf|strcat|memmove|wcsncpy|wcscpy|snprintf|_snprintf|strncat|wcsncat|wcscat|wmemmove|wmemcpy").argument(1)
  
  // We track flow to the Base Pointer (Argument 1) of the Index Access
  def loopSinks = cpg.call("<operator>.indirectIndexAccess|<operator>.indexAccess").argument(1)
  
  // Combine Sinks
  def sinks = standardSinks ++ loopSinks
  
  // Run Flow Query
  val flows = sinks.reachableByFlows(sources).l
  
  val results = flows.map { flow =>
    // Extract metadata from the flow
    val sourceNode = flow.elements.head.asInstanceOf[io.shiftleft.codepropertygraph.generated.nodes.Expression]
    val sinkNode = flow.elements.last
    
    // Safely get method name using traversal
    val methodNode = sourceNode.start.method.head
    
    // Get all line numbers involved in the flow (Nodes in the path)
    val flowLines = flow.elements.map(_.lineNumber).filter(_.isDefined).map(_.get)
    
    // Find definitions for variables in the locations where they are used.
    
    // Find definitions in the Source Method (Start) and Sink Method (End)
    
    val sourceMethod = sourceNode.start.method.head
    val sinkMethod = sinkNode match {
       case e: Expression => e.start.method.head
       case _ => sourceMethod
    }
    
    val methodsToCheck = Set(sourceMethod, sinkMethod)
    
    val flowNames = flow.elements.collect { case id: Identifier => id.name }.toSet
    
    val sinkCallNames = sinkNode match {
      case arg: Expression => 
        arg.astParent match {
          case call: Call => 
             call.argument.collect { case id: Identifier => id.name }.toSet
          case _ => Set.empty[String]
        }
      case _ => Set.empty[String]
    }
    
    val targetNames = flowNames ++ sinkCallNames
    
    val defLines = methodsToCheck.flatMap { m =>
      val locals = m.local.filter(l => targetNames.contains(l.name)).map(_.lineNumber).filter(_.isDefined).map(_.get).l
      val params = m.parameter.filter(p => targetNames.contains(p.name)).map(_.lineNumber).filter(_.isDefined).map(_.get).l
      locals ++ params
    }
    
    // Combine and Sort
    val lines = (flowLines ++ defLines).distinct.sorted
    
    // Determine Label based on Method Name Convention
    val methodName = methodNode.name
    val label = if (methodName.toLowerCase.contains("bad") && !methodName.toLowerCase.contains("good")) 1 else 0
    
    Map(
      "method" -> methodName,
      "file" -> methodNode.filename,
      "label" -> label,
      "lines" -> lines.mkString(","),
      "source_func" -> sourceNode.code,
      "sink_func" -> sinkNode.code
    )
  }
  
  import java.io._
  val pw = new PrintWriter(new File(outFile))
  results.foreach { res =>
    val json = s"""{
      |  "method": "${res("method")}",
      |  "file": "${res("file")}",
      |  "label": ${res("label")},
      |  "lines": [${res("lines")}],
      |  "source": "${res("source_func").toString.replace("\"", "\\\"")}",
      |  "sink": "${res("sink_func").toString.replace("\"", "\\\"")}"
      |}""".stripMargin.replaceAll("[\r\n]+", " ")
    pw.println(json)
  }
  pw.close()
  
  println(s"Extracted ${results.size} gadgets to $outFile")
}
