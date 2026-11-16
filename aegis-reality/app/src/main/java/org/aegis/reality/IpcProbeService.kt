package org.aegis.reality

import android.app.Service
import android.content.Intent
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.Message
import android.os.Messenger
import android.os.Process

class IpcProbeService : Service() {
    private val messenger by lazy {
        Messenger(Handler(Looper.getMainLooper()) { message: Message ->
            val reply = message.replyTo
            if (reply != null) {
                val response = Message.obtain(null, message.what)
                response.arg1 = Process.myPid()
                response.arg2 = Process.myUid()
                reply.send(response)
            }
            true
        })
    }

    override fun onBind(intent: Intent?): IBinder = messenger.binder
}
