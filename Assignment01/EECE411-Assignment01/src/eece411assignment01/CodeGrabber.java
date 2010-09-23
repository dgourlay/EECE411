/*
 *  UBC EECE 411 - Assignment 01
 *
 *  Author: Derek Gourlay, 66435041
 *  Date: Thursday, September 23, 2010
 *
 * Usage, call from commandline with arguements: server address, port number, student number
 *
 */
package eece411assignment01;

import eece411assignment01.util.ByteOrder;
import eece411assignment01.util.StringUtils;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.net.SocketException;

public class CodeGrabber {

    /**
     * @param args the command line arguments
     */
    private static int DEFAULT_PORT = 5627;
    private String codeResult = null;

    public CodeGrabber(String[] args) throws IOException {

        String server = args[0];       // Server name or IP address
        int servPort = (args.length == 3) ? Integer.parseInt(args[1]) : DEFAULT_PORT; //user specified port or default #
        int studentNum = (args.length == 3) ? Integer.parseInt(args[2]) : Integer.parseInt(args[1]); //student num to send to server


        System.out.println("Attempting to connect to " + server + ":" + servPort + " ...");

        // Create socket that is connected to server on specified port

        Socket socket = null;
        try {
            socket = new Socket(server, servPort);
        } catch (IOException iOException) {
            System.out.println("Error setting up socket connection...");
            iOException.printStackTrace();

        }

        System.out.println("Successfully connected to server " + server + " (" + socket.getInetAddress() + ")!");

        //Setup in/out streams to/from the server
        InputStream in = socket.getInputStream();
        OutputStream out = socket.getOutputStream();

        //send the server the studentNumber in little endian format
        ByteOrder.int2leb(studentNum, out);


        //Get the message size and code length
        byte[] responseBuffer = new byte[12];

        int totalBytesRcvd = 0;  // Total bytes received so far
        int bytesRcvd;           // Bytes received in last read

        while (totalBytesRcvd < responseBuffer.length) {
            if ((bytesRcvd = in.read(responseBuffer, totalBytesRcvd,
                    responseBuffer.length - totalBytesRcvd)) == -1) {
                throw new SocketException("Connection close prematurely");
            }
            totalBytesRcvd += bytesRcvd;
        }

        int msgLength = ByteOrder.leb2int(responseBuffer, 0);
        int codeLength = ByteOrder.leb2int(responseBuffer, 8);

        System.out.println("Message Length: " + msgLength);
        System.out.println("Code Length: " + codeLength);

        //get remaining portion of the message
        byte[] remainBuffer = new byte[msgLength - 12];
        totalBytesRcvd = 0;
        bytesRcvd = 0;

        while (totalBytesRcvd < remainBuffer.length) {
            if ((bytesRcvd = in.read(remainBuffer, totalBytesRcvd,
                    remainBuffer.length - totalBytesRcvd)) == -1) {
                throw new SocketException("Connection close prematurely");
            }
            totalBytesRcvd += bytesRcvd;
        }

        //extract the code
        byte[] codeBuffer = new byte[codeLength];

        for (int i = 0, index = remainBuffer.length - codeLength; i < codeLength; i++, index++) {
            codeBuffer[i] = remainBuffer[index];
        }

        String code = StringUtils.byteArrayToHexString(codeBuffer);

        setCodeResult(code);  //set variable for JUnit testing

        System.out.println("The secret code is: " + code);



        try {
            // Close the socket and its streams
            socket.close();
        } catch (IOException iOException) {
            System.out.println("Error closing socket...");
            iOException.printStackTrace();
        }


    }

    public static void main(String[] args) {

        try {
            CodeGrabber mainProgram = new CodeGrabber(args);
        } catch (IOException iOException) {
            System.out.println("General error running program...");
            iOException.printStackTrace();
        }

    }

    /**
     * @return the codeResult
     */
    public String getCodeResult() {
        return codeResult;
    }

    /**
     * @param codeResult the codeResult to set
     */
    public void setCodeResult(String codeResult) {
        this.codeResult = codeResult;
    }
}
