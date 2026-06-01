// pages/index/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    loading: true,
    hasTask: false,
    location: '',
    timeRange: '',
    isCheckedIn: false,
    status: '',
    recordId: null,
    unreadCount: 0 ,
  },
  //检查任务
  fetchTodayTask(){
    const token = wx.getStorageSync('token');
    
     // 先检查token是否合格
    if(!token){
      wx.redirectTo({url:'/pages/login/login'})  //token如果不合格重新跳回登录界面
      return
    }
    wx.request({
      url: 'http://121.41.20.177:8000/duty/duty_task',
      method:'GET',
      header:{'Authorization': `Bearer ${token}`},  //接收后端token
      success:(res)=>{
        if(res.statusCode==200){      //先检查是否请求失败，200可以进行下一步
            var data=res.data;      //把接收到的后端数据赋值给前端的data
            var start = data.start_time || "未设置";
            var end = data.end_time || "未设置";
            var timeRange = `${start}-${end}`;
            this.setData({
                loading:false,
                hasTask:data.has_task,
                isCheckedIn:data.is_checked_in,
                location:data.location,
                status:data.status,
                timeRange:timeRange,
                recordId:data.record_id
            })
        }
        else if(res.statusCode==401){
             wx.removeStorageSync('token');
             wx.redirectTo({url:'/pages/login/login'})
        }
        else{
          wx.showToast({
             title:'获取任务失败',icon:'none'
          })
        }
      },
      fail:()=>{
          wx.showToast({
            title:'请求网络失败',icon:'none'
          })
      }
    })

  },
  //跳转相机页面
  goCamera(){
  const recordId=this.data.recordId;
  if (! recordId){
    wx.showToast({title:'没有获取任务',icon:'none'})
    return 
  };
  wx.navigateTo({
    url: `/pages/camera/camera?recordId=${recordId}`
  });
  },
   // ===== 新增：获取未读通知数 =====
   fetchUnreadCount() {
    const token = wx.getStorageSync('token');
    if (!token) return;
    wx.request({
      url: 'http://121.41.20.177:8000/duty/notifications',
      method: 'GET',
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const notifications = res.data.notifications || [];
          const unread = notifications.filter(n => !n.is_read).length;
          this.setData({ unreadCount: unread });
        }
      }
    });
  },
  // ===== 新增：跳转到通知页面 =====
  goNotifications() {
    wx.navigateTo({ url: '/pages/notifications/notifications' });
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
   this.fetchTodayTask();
   this.fetchUnreadCount();                        
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.fetchTodayTask();
    this.fetchUnreadCount();
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})