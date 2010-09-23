/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package eece411assignment01;

import eece411assignment01.util.ByteOrder;
import eece411assignment01.util.StringUtils;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;

/**
 *
 * @author dgourlay
 */
public class Main {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws IOException {
        String server = args[0];       // Server name or IP address
        int servPort = (args.length == 3) ? Integer.parseInt(args[1]) : 5627;
        int studentNum = (args.length == 3) ? Integer.parseInt(args[2]) : Integer.parseInt(args[1]);
        //byte[] byteBuffer = (args.length == 3) ? args[2].getBytes() : args[1].getBytes();


        System.out.println("Attempting to connect to " + server + ":" + servPort + " ...");
        // Create socket that is connected to server on specified port
        Socket socket = new Socket(server, servPort);
        System.out.println("Successfully connected to server " + server + " (" + socket.getInetAddress() + ")!");


        InputStream in = socket.getInputStream();
        OutputStream out = socket.getOutputStream();

        ByteOrder.int2leb(studentNum, out);

        /*
        byte[] response = new byte[100];
        int byteCount=0;
        while(in.read(response) != -1){
            byteCount++;
        }
         *
         */


        BufferedReader inReader = new BufferedReader(new InputStreamReader(
                in));

        byte[] byteBuffer = {};

        String responseString = inReader.readLine();
        byte[] responseBuffer = responseString.getBytes();

        
        int msgLength = ByteOrder.leb2int(responseBuffer, 0, 4);

        System.out.println("Message length: " + msgLength);

        int codeLength = ByteOrder.leb2int(responseBuffer, 8, 4);
        System.out.println("Code length: " + codeLength);

        byte[] codeArray = new byte[codeLength];

        int index=0;
        for(int i = msgLength - codeLength -1; i < msgLength; i++,index++){
            codeArray[index]=responseBuffer[i];
        }


        System.out.println(StringUtils.byteArrayToHexString(codeArray));
        
        //int secretCode = ByteOrder.leb2int(responseBuffer, responseBuffer.length - codeLength);


        //      System.out.println("Code: "+codeString);

         
        socket.close();  // Close the socket and its streams

    }
}
