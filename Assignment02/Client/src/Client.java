/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 *
 * @author dgourlay
 */
public interface Client extends Remote {

	void receive(String s) throws RemoteException;

    
}
