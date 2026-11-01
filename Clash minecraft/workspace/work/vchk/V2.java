public class V2 { public static void main(String[] a) throws Exception {
  for (String n : new String[]{"kr.kjmn.clashmc.CardDef","kr.kjmn.clashmc.Clash","kr.kjmn.clashmc.Clash$1"}) {
    Class<?> c = Class.forName(n, true, V2.class.getClassLoader()); c.getDeclaredMethods(); System.out.println("verified " + n); } } }
