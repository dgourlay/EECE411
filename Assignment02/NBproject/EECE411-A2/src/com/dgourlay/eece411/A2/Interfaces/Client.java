/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.dgourlay.eece411.A2.Interfaces;

import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 *
 * @author dgourlay
 */
public interface Client extends Remote {

    void receive(String s) throws RemoteException;
    
}
