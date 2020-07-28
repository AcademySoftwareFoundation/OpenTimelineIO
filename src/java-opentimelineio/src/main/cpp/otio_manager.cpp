#include <otio_manager.h>
#include <utilities.h>

struct KeepaliveMonitor
{
    OTIO_NS::SerializableObject* _so;
    jobject                      _keep_alive;
    JNIEnv*                      _env;

    KeepaliveMonitor(JNIEnv* env, OTIO_NS::SerializableObject* so)
        : _so(so), _env(env)
    {}

    void monitor()
    {
        if(_so->current_ref_count() > 1)
        {
            if(!_keep_alive)
            { _keep_alive = serializableObjectFromNative(_env, _so); }
        }
        else
        {
            if(_keep_alive)
            {
                _keep_alive = nullptr; // this could cause destruction
            }
        }
    }
};

void
install_external_keepalive_monitor(
    JNIEnv* env, OTIO_NS::SerializableObject* so, bool apply_now)
{
    KeepaliveMonitor m(env, so);
    using namespace std::placeholders;
    // printf("Install external keep alive for %p: apply now is %d\n", so, apply_now);
    so->install_external_keepalive_monitor(
        std::bind(&KeepaliveMonitor::monitor, m), apply_now);
}