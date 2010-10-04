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
public interface Server extends Remote {

    void register(Client c) throws RemoteException;

    void send_message(String s) throws RemoteException;
}
