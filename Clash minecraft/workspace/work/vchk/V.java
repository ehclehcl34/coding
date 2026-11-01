public class V { public static void main(String[] a) throws Exception {
  for (String n : new String[]{"kr.kjmn.clashmc.Combatant","kr.kjmn.clashmc.Combatant$Kind","kr.kjmn.clashmc.Battle","kr.kjmn.clashmc.Battle$1","kr.kjmn.clashmc.Battle$2","kr.kjmn.clashmc.Battle$3","kr.kjmn.clashmc.Battle$4","kr.kjmn.clashmc.Battle$Zone"}) {
    Class<?> c = Class.forName(n, true, V.class.getClassLoader()); c.getDeclaredMethods(); System.out.println("verified " + n);
  } } }
