
import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;
import java.util.LinkedList;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author dgourlay
 */
public class ServerImpl extends UnicastRemoteObject implements Server {

    private LinkedList<Client> clientList;


    public ServerImpl() throws RemoteException {
        clientList = new LinkedList<Client>();

    }

    public synchronized void register(Client c) throws RemoteException {
        clientList.add(c);
    }

    public synchronized void send_message(String msg, Client c) throws RemoteException {
        for(Client cs : clientList){
			if(!cs.equals(c) ){
				cs.receive(msg);
			}
		}
    }

    public static void main(String[] args) {
        try {
            Naming.rebind("Server", new ServerImpl());
        } catch (Exception e) {
            System.out.println("Error Binding");
            e.printStackTrace();
        }
    }
}
