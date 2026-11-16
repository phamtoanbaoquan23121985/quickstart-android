package org.aegis.reality

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Message
import android.os.Messenger
import android.os.Process
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

@RunWith(AndroidJUnit4::class)
class PrivateIpcBoundaryTest {
    @Test
    fun privateSecondaryProcessRespondsAcrossMessengerBinderBoundary() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val connected = CountDownLatch(1)
        val replied = CountDownLatch(1)
        val remotePid = AtomicInteger(-1)
        val remoteUid = AtomicInteger(-1)
        var service: Messenger? = null

        val connection = object : android.content.ServiceConnection {
            override fun onServiceConnected(name: ComponentName, binder: android.os.IBinder) {
                service = Messenger(binder)
                connected.countDown()
            }

            override fun onServiceDisconnected(name: ComponentName) {
                service = null
            }
        }

        val intent = Intent().setComponent(
            ComponentName(context, IpcProbeService::class.java)
        )
        assertNotNull(context.packageManager)
        assertEquals(true, context.bindService(intent, connection, Context.BIND_AUTO_CREATE))
        try {
            assertEquals(true, connected.await(10, TimeUnit.SECONDS))
            val request = Message.obtain(null, 7)
            request.replyTo = Messenger(android.os.Handler(
                InstrumentationRegistry.getInstrumentation().targetContext.mainLooper
            ) { response ->
                remotePid.set(response.arg1)
                remoteUid.set(response.arg2)
                replied.countDown()
                true
            })
            service?.send(request)
            assertEquals(true, replied.await(10, TimeUnit.SECONDS))
            assertNotEquals(Process.myPid(), remotePid.get())
            assertEquals(Process.myUid(), remoteUid.get())
        } finally {
            context.unbindService(connection)
        }
    }
}
