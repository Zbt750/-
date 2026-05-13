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
    canvasWidth: 0,  // 默认宽度，稍后会根据实际图片缩放调整
    canvasHeight: 0, // 默认高度
    unreadCount: 0 ,
    showCamera:false,
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
      url: 'http://127.0.0.1:8000/duty/duty_task',
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
  //如果没有打卡拍照
  take_Photo_CheckIn(){
   var ctx=wx.createCameraContext();//调用相机
   ctx.takePhoto({
    quality:'high',
    success:(res)=>{
    var tempImagePath= res.tempImagePath;//相片的临时路径
    //然后把临时路径给水印的函数
    this.addWaterMark(tempImagePath);
   },
   fail:()=>{
    wx.showToast({title:'拍照失败',icon:'none'})
   }
   });
  },
  //拍照相加
  startCamera(){
  this.setData({showCamera:true})
  },
  //关闭摄像头
  cancelCamera(){
 this.setData({showCamera:false})
  },
  //添加照片水印
   
    addWaterMark(imagePath){
      var that = this;
      //学生信息
      var userInfo = {
        name: wx.getStorageSync('name') || '学生',
        student_id: wx.getStorageSync('student_id') || ''
      };
      //时间修复：getFullYear()等需要括号，getDay()改为getDate()
      var now = new Date();
      var dateStr = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;
  
      // 1. 获取 Canvas 节点 (核心修复：必须先获取 canvas 对象)
      const query = wx.createSelectorQuery();
      query.select('#watermarkCanvas')
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res[0]) {
            wx.showToast({ title: 'Canvas 节点获取失败', icon: 'none' });
            return;
          }
          
          const canvas = res[0].node; // 定义 canvas 变量
          const ctx = canvas.getContext('2d'); // 获取绘图上下文 (不是 createImage)
  
          // 2. 创建图片对象
          const img = canvas.createImage();
          img.src = imagePath;
  
          // 3. 图片加载完成后绘制
          img.onload = () => {
            // 设置画布尺寸与原图一致
            canvas.width = img.width;
            canvas.height = img.height;
  
            // 绘制原图 (使用 ctx.drawImage)
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);//📌 总结：为什么这么写？
            // 你可以把这个过程想象成在墙上画画：
            // createSelectorQuery：去物业（小程序系统）申请查看墙面的权限。
            // canvas = res[0].node：拿到墙面的钥匙（拿到画板对象）。
            // createImage：去打印店把你要画的照片打印出来（创建图片对象）。
            // img.onload：等打印店把照片打印好（等待异步加载完成）。
            // drawImage：把打印好的照片贴在墙上（绘制到画布）。
  

            // 绘制文字 (新版 API 直接赋值属性)
            ctx.fillStyle = 'white'; 
            ctx.font = 'bold 30px sans-serif'; // 设置字体大小
            ctx.shadowColor = "rgba(0, 0, 0, 0.5)"; // 文字阴影，增加可读性
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 5;
            ctx.shadowOffsetY = 5;
  
            ctx.fillText(`${userInfo.name}(${userInfo.student_id})`, 20, canvas.height - 100);
            ctx.fillText(`打卡时间: ${dateStr}`, 20, canvas.height - 60);
            ctx.fillText(`打扫状态: 已打扫`, 20, canvas.height - 20);
  
            // 4. 导出图片 (新版 API 不需要 draw() 方法，也不需要 setTimeout)
            wx.canvasToTempFilePath({
              canvas: canvas, // 传入 canvas 对象，不是 canvasId
              success: (res) => {
                var watermarkPath = res.tempFilePath;
                //调用上传这个照片
                that.uploadImage(watermarkPath);
              },
              fail: (err) => {
                console.error('导出水印照片失败', err);
                wx.showToast({ title: '合成水印失败', icon: 'none' });
              }
            }, that);
          };
          
          img.onerror = (err) => {
              console.error('图片加载失败', err);
              wx.showToast({ title: '图片加载失败', icon: 'none' });
          }
        });
    },
  //上传照片
  uploadImage(watermarkPath){
    var token=wx.getStorageSync('token');
    wx.uploadFile({
      filePath: watermarkPath,//获取文件路径
      name: 'file',//这是为了后端上传接口的名字相同
      url: 'http://127.0.0.1:8000/upload/upload_watermark',
      //先验证token是否合法
      header:{'Authorization':`Bearer ${token}`},
      success:(res)=>{
        console.log('上传接口返回的数据：', data);
        //先把这个图片的文件转换成为JSON格式
        var data=JSON.parse(res.data)
        //再把这个转换成的数据给这个打卡的变量
        var photourl= data.url || data.data || res.data;
        var base64 = data.base64 || '';
        //提交打卡(把图片上传打卡)
        this.incheck(photourl,base64);
      },
      fail:()=>{
        wx.showToast({title:'上传失败',icon:'none'})
      }
    })
  },


  //打卡,需要发送请求post提交
  incheck(photo,base64){
   //先验证token合法性
   var token=wx.getStorageSync('token')
   wx.request({
    url:'http://127.0.0.1:8000/duty/submit_watermark',
    method:'POST',
    header:{'Authorization':`Bearer ${token}`},
    data:{
     watermark_url:photo,
     record_id:this.data.recordId,
     base64_data: base64 || '',
    },
    success:(res)=>{
      //查看状态是否打卡成功
      if(res.statusCode==200){
        wx.showToast({title:'打卡成功',icon:'success'});
        //并且重新刷新任务界面
        showCamera:false;
        isCheckedIn:true;
        this.fetchTodayTask();
      }
      else{
         wx.showToast({title:'打卡失败',icon:'none'});
      }
    },
    fail:()=>{
     wx.showToast({title:'网路错误',icon:'none'});
    }
   })
  },
   // ===== 新增：获取未读通知数 =====
   fetchUnreadCount() {
    const token = wx.getStorageSync('token');
    if (!token) return;
    wx.request({
      url: 'http://127.0.0.1:8000/duty/notifications',
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