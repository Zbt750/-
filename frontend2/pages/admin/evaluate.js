// pages/admin/evaluate.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    task:{},
    isEvaluated:false,
    loading:true,
    currentStatus:'',
    recordId: null,
    isUnqualified: false,
    reason: '',
    showReasonInput: false,
  },
 
  // 获取评论详细任务
  fetchTaskDetail(){
  //  判断token
   const token=wx.getStorageSync('token')
   wx.request({
    url:'http://121.41.20.177:8000/admin/get_admin_tasks',
    method:'GET',
    header: { 'Authorization': `Bearer ${token}` },
    success:(res)=>{
      // 如果请求成功
      if (res.statusCode==200){
        const tasks=res.data.tasks;
        const task=tasks.find(t=>t.record_id==this.data.recordId);
        // 如果任务存在
        if(task){
          const isEvaluated = task.is_evaluated
          this.setData({
            task:task,
            isEvaluated:isEvaluated,
            loading:false,
            currentStatus:task.status
          })
        }
        // 如果任务不存在
        else{
          wx.showToast({title:'任务未找到',icon:'none'})
          this.setData({
            loading:false
          })
        }
      }
      // 如果请求失败
      else{
        wx.showToast({title:'请求获取失败',icon:'none'})
        this.setData({
          loading:false
        })
      }
    },
    fail:()=>{
      wx.showToast({title:'网路异常',icon:'none'})
    }
   })
  },
//按钮 标记是否及格
  markQualified() {
    console.log('markQualified 被调用');
    if (this.data.isEvaluated) {
      wx.showToast({ title: '该任务已评价', icon: 'none' });
      return;
    }
    this.setData({ isUnqualified: false, showReasonInput: false });
    this.submitEvaluate();
  },
  // 按钮标记是否不及格
  markUnqualified() {
    if (this.data.isEvaluated) {
      wx.showToast({ title: '该任务已评价', icon: 'none' });
      return;
    }
    this.setData({ isUnqualified: true, showReasonInput: true });
  },
  // 不合格原因输入
  onReasonInput(e) {
    this.setData({ reason: e.detail.value });
  },

  // 提交评价
  submitEvaluate(){    
  const token=wx.getStorageSync('token')
  const data={record_id:this.data.recordId,
  is_unqualified:this.data.isUnqualified}
  console.log('发送的数据：', data);
  // 如果当前数据是不合格但是没有写原因
  if(this.data.isUnqualified && !this.data.reason && !this.data.reason){
    wx.showToast({
      title: '请写入不合格的原因',
      icon:'none'
    });
    return;
  }
  // 如果仅仅是判断不合格
  if(this.data.isUnqualified){
    data.reason=this.data.reason
  }
  wx.request({
    url:'http://121.41.20.177:8000/admin/evaluate',
    method:'POST',
    header: { 'Authorization': `Bearer ${token}` },
    data:data,
    success:(res)=>{
      if(res.statusCode==200){
        wx.showToast({ title: '评价成功', icon: 'success' });
        wx.navigateBack(); // 返回列表页
      }
      else{
        wx.showToast({ title: res.data.detail || '评价失败', icon: 'none' })
      }
    },
    fail:()=>{
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  })

  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.setData({ recordId: parseInt(options.recordId) });
    this.fetchTaskDetail();
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