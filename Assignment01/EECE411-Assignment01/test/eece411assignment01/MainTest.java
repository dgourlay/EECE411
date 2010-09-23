/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package eece411assignment01;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author dgourlay
 */
public class MainTest {

    public MainTest() {
    }

    @BeforeClass
    public static void setUpClass() throws Exception {
    }

    @AfterClass
    public static void tearDownClass() throws Exception {
    }

    /**
     * Test of main method, of class Main.
     */
    @Test
    public void testMain() throws Exception {
        System.out.println("main");

        String[] args = {"reala.ece.ubc.ca","5627","909090"};
        System.out.println("* MainTest");

        CodeGrabber g = new CodeGrabber(args);

        //Test for propert output
        assertEquals("15FCA0902715E21BE540F257E5ED1388C43A498C", g.getCodeResult());

    }

}