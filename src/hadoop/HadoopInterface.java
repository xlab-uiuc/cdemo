package hadoop;

import soot.RefType;
import soot.SootClass;
import soot.SootMethod;
import soot.Value;
import soot.jimple.InstanceInvokeExpr;
import soot.jimple.InvokeExpr;
import soot.jimple.StaticInvokeExpr;
import soot.jimple.VirtualInvokeExpr;

public class HadoopInterface {	
  public static final String superConfigClass = "org.apache.hadoop.conf.Configuration";
  
  /**
   * Return if the given class is a subclass that inherits the superConfigClass
   * @param cls
   * @return
   */
  public static boolean isSubClass(SootClass cls) {
    if (cls.toString().contains(superConfigClass)) {
      return true;
    }
    if (cls.hasSuperclass() && cls.getSuperclass().toString().contains(superConfigClass)) {
      return true;
    }
    return false;
  }
  
  /**
   * Return if the statement is a getter statement
   * @param iexpr
   * @return
   */
  public static boolean isGetter(InvokeExpr iexpr) {
    SootMethod callee = iexpr.getMethod();
    if (callee.getName().startsWith("get")) {
      if (iexpr instanceof InstanceInvokeExpr) {
        Value base = ((InstanceInvokeExpr) iexpr).getBase();
        if (base.getType() instanceof RefType) {
          RefType rty = (RefType) base.getType();
          if (isSubClass(rty.getSootClass())) {
            return true;
          }
        }
      } else if (iexpr instanceof StaticInvokeExpr) {
        // pass
      } else if (iexpr instanceof VirtualInvokeExpr) {
        // pass
      }
    }
    return false;
  }
}
